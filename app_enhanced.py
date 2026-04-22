from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, session, url_for, send_file, jsonify, Response
import subprocess, os, json, base64, time
from datetime import datetime, timedelta
import threading
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import face_recognition
    import cv2
    import numpy as np
    FACE_RECOGNITION_ENABLED = True
except ImportError:
    FACE_RECOGNITION_ENABLED = False
    print("Face recognition not available.")

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_ENABLED = True
except ImportError:
    GOOGLE_ENABLED = False
    print("Google API libraries not available.")

# Flask App
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

# Paths
STUDENT_DATA_FILE = 'students_data.json'
SUBJECTS_FILE = 'subjects.json'
ATTENDANCE_FOLDER = 'attendance_logs'
STUDENT_PHOTOS_FOLDER = 'student_photos'
DATA_FOLDER = 'data'
EXCEL_FILE_PATH = 'attendance_backup.xlsx'

os.makedirs(ATTENDANCE_FOLDER, exist_ok=True)
os.makedirs(STUDENT_PHOTOS_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID', '1VAth6jc2rWlUhpSpL7WhrB8ryTiz6d6bd1jgn37i0uE')
GOOGLE_DRIVE_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER_ID', '146S39x63_ycnNpv9vgtLOE18cx-54ghG')

SHEETS_ENABLED = False
gc = None
spreadsheet = None

if GOOGLE_ENABLED:
    try:
        creds_b64 = os.environ.get('GOOGLE_CREDS_B64')
        if creds_b64:
            creds_json = base64.b64decode(creds_b64).decode('utf-8')
            credentials = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
            gc = gspread.authorize(credentials)
            spreadsheet = gc.open_by_key(GOOGLE_SHEET_ID)
            SHEETS_ENABLED = True
            print("Google Sheets connected successfully")
    except Exception as e:
        print(f"Google Sheets initialization failed: {e}")

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'bcca')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'bcca')

# ============================
# Helper Functions
# ============================

def load_students():
    """Load student data from JSON file"""
    if os.path.exists(STUDENT_DATA_FILE):
        with open(STUDENT_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_students(students):
    """Save student data to JSON file"""
    with open(STUDENT_DATA_FILE, 'w') as f:
        json.dump(students, f, indent=2)

def load_subjects():
    """Load subjects from JSON file"""
    if os.path.exists(SUBJECTS_FILE):
        with open(SUBJECTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_subjects(subjects):
    """Save subjects to JSON file"""
    with open(SUBJECTS_FILE, 'w') as f:
        json.dump(subjects, f, indent=2)

def get_attendance_data(subject=None):
    """Get attendance data from logs"""
    attendance_data = {}
    if os.path.exists(ATTENDANCE_FOLDER):
        for filename in os.listdir(ATTENDANCE_FOLDER):
            if filename.endswith('.json'):
                filepath = os.path.join(ATTENDANCE_FOLDER, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if subject is None or data.get('subject') == subject:
                        attendance_data[data['date']] = data
    return attendance_data

def upload_to_drive(file_path, file_name):
    """Upload file to Google Drive"""
    if not SHEETS_ENABLED:
        return None
    try:
        drive_service = build('drive', 'v3', credentials=credentials)
        file_metadata = {'name': file_name, 'parents': [GOOGLE_DRIVE_FOLDER_ID]}
        media = MediaFileUpload(file_path, mimetype='image/png')
        uploaded = drive_service.files().create(
            body=file_metadata, media_body=media, fields='id'
        ).execute()
        return uploaded.get('id')
    except Exception as e:
        print(f"Drive upload failed: {e}")
        return None

def update_excel_attendance(date, subject, present_students, all_students):
    """Update Excel file with attendance"""
    try:
        if os.path.exists(EXCEL_FILE_PATH):
            df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=None)
        else:
            df = {}
        
        sheet_name = subject if subject else "General"
        if sheet_name not in df:
            df[sheet_name] = pd.DataFrame(columns=['Name', 'Roll No'])
        
        sheet_df = df[sheet_name]
        if date not in sheet_df.columns:
            sheet_df[date] = 'Absent'
        
        for student in all_students:
            if student not in sheet_df['Name'].values:
                new_row = pd.DataFrame([[student, all_students[student].get('roll_no', '')]], 
                                     columns=['Name', 'Roll No'])
                sheet_df = pd.concat([sheet_df, new_row], ignore_index=True)
        
        for student in present_students:
            sheet_df.loc[sheet_df['Name'] == student, date] = 'Present'
        
        df[sheet_name] = sheet_df
        
        with pd.ExcelWriter(EXCEL_FILE_PATH, engine='openpyxl') as writer:
            for sheet, data in df.items():
                data.to_excel(writer, sheet_name=sheet, index=False)
        
        return True
    except Exception as e:
        print(f"Excel update error: {e}")
        return False

# ============================
# Background Scheduler
# ============================

# Global flag for scheduled attendance trigger
scheduled_trigger = {'active': False, 'subject': '', 'triggered_at': None}

def schedule_attendance():
    """Background thread - sets flag when scheduled time hits"""
    while True:
        try:
            if os.path.exists('attendance_time.json'):
                with open('attendance_time.json', 'r') as f:
                    data = json.load(f)
                    time_str = data.get('time')
                    subject = data.get('subject', '')
                    if time_str:
                        now = datetime.now()
                        schedule_time = datetime.strptime(time_str, '%H:%M').replace(
                            year=now.year, month=now.month, day=now.day
                        )
                        if now >= schedule_time and now < schedule_time + timedelta(minutes=1):
                            if not scheduled_trigger['active']:
                                print(f"Scheduled attendance triggered for {subject}...")
                                scheduled_trigger['active'] = True
                                scheduled_trigger['subject'] = subject
                                scheduled_trigger['triggered_at'] = now.strftime('%H:%M')
                            time.sleep(60)
        except Exception as e:
            print(f"Scheduler error: {e}")
        time.sleep(10)

threading.Thread(target=schedule_attendance, daemon=True).start()

# ============================
# Authentication Routes
# ============================

@app.route('/', methods=['GET', 'POST'])
def login():
    """Login page for both admin and students"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user_type = request.form.get('user_type', 'admin')
        
        if user_type == 'admin':
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['user'] = 'admin'
                session['user_type'] = 'admin'
                return redirect('/admin/dashboard')
            else:
                return render_template('login.html', error="Invalid admin credentials")
        else:
            # Student login
            students = load_students()
            if username in students:
                student = students[username]
                if student.get('password') == password:
                    session['user'] = username
                    session['user_type'] = 'student'
                    return redirect('/student/dashboard')
            return render_template('login.html', error="Invalid student credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ============================
# Admin Routes
# ============================

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard with statistics"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    students = load_students()
    subjects = load_subjects()
    msg = request.args.get('msg')
    
    # Calculate statistics
    total_students = len(students)
    total_subjects = len(subjects)
    
    # Get today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    today_file = os.path.join(ATTENDANCE_FOLDER, f"{today}.json")
    today_present = 0
    if os.path.exists(today_file):
        with open(today_file, 'r') as f:
            data = json.load(f)
            today_present = len(data.get('present', []))
    
    return render_template('admin_dashboard.html',
                         msg=msg,
                         total_students=total_students,
                         total_subjects=total_subjects,
                         today_present=today_present,
                         sheets_enabled=SHEETS_ENABLED,
                         face_recognition_enabled=FACE_RECOGNITION_ENABLED)

@app.route('/admin/students')
def admin_students():
    """View all students"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    students = load_students()
    student_list = []
    for username, data in students.items():
        student_list.append({
            'username': username,
            'name': data.get('name', ''),
            'roll_no': data.get('roll_no', ''),
            'class': data.get('class', ''),
            'semester': data.get('semester', ''),
            'photo': f"/student_photo/{username}"
        })
    
    return render_template('admin_students.html', students=student_list)

@app.route('/admin/add_student', methods=['GET', 'POST'])
def admin_add_student():
    """Add new student"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            name = request.form.get('name', '').strip()
            roll_no = request.form.get('roll_no', '').strip()
            class_name = request.form.get('class', '').strip()
            semester = request.form.get('semester', '').strip()
            password = request.form.get('password', '').strip()
            photo_data = request.form.get('photo', '')
            
            if not all([username, name, roll_no, class_name, semester, password, photo_data]):
                return render_template('admin_add_student.html', error="All fields are required")
            
            students = load_students()
            if username in students:
                return render_template('admin_add_student.html', error="Username already exists")
            
            # Save photo
            header, encoded = photo_data.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            
            photo_path = os.path.join(STUDENT_PHOTOS_FOLDER, f"{username}.png")
            with open(photo_path, 'wb') as f:
                f.write(image_bytes)
            
            data_path = os.path.join(DATA_FOLDER, f"{username}.png")
            with open(data_path, 'wb') as f:
                f.write(image_bytes)
            
            # Verify face
            if FACE_RECOGNITION_ENABLED:
                image = face_recognition.load_image_file(data_path)
                face_encodings = face_recognition.face_encodings(image)
                if len(face_encodings) == 0:
                    os.remove(photo_path)
                    os.remove(data_path)
                    return render_template('admin_add_student.html', error="No face detected in photo")
            
            # Upload to Google Drive
            if SHEETS_ENABLED:
                upload_to_drive(photo_path, f"{username}.png")
            
            # Save student data
            students[username] = {
                'name': name,
                'roll_no': roll_no,
                'class': class_name,
                'semester': semester,
                'password': password
            }
            save_students(students)
            
            return redirect(url_for('admin_dashboard', msg=f"Student {name} added successfully"))
        
        except Exception as e:
            return render_template('admin_add_student.html', error=str(e))
    
    return render_template('admin_add_student.html')

@app.route('/admin/remove_student', methods=['GET', 'POST'])
def admin_remove_student():
    """Remove student"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    students = load_students()
    
    if request.method == 'POST':
        username = request.form.get('username')
        if username and username in students:
            # Remove files
            for folder in [STUDENT_PHOTOS_FOLDER, DATA_FOLDER]:
                photo_path = os.path.join(folder, f"{username}.png")
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            
            # Remove from data
            del students[username]
            save_students(students)
            
            return redirect(url_for('admin_dashboard', msg=f"Student removed successfully"))
    
    return render_template('admin_remove_student.html', students=students)

@app.route('/admin/subjects', methods=['GET'])
def admin_subjects():
    """View all subjects"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    subjects = load_subjects()
    return render_template('admin_subjects.html', subjects=subjects)

@app.route('/admin/add_subject', methods=['GET', 'POST'])
def admin_add_subject():
    """Add new subject"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    if request.method == 'POST':
        subject_code = request.form.get('subject_code', '').strip()
        subject_name = request.form.get('subject_name', '').strip()
        
        if subject_code and subject_name:
            subjects = load_subjects()
            if not any(s['code'] == subject_code for s in subjects):
                subjects.append({'code': subject_code, 'name': subject_name})
                save_subjects(subjects)
                return redirect(url_for('admin_subjects'))
    
    return render_template('admin_add_subject.html')

@app.route('/admin/remove_subject', methods=['GET', 'POST'])
def admin_remove_subject():
    """Remove a subject"""
    if session.get('user_type') != 'admin':
        return redirect('/')

    subjects = load_subjects()

    if request.method == 'POST':
        subject_code = request.form.get('subject_code')
        if not subject_code:
            return render_template('admin_remove_subject.html', subjects=subjects, error="Please select a subject")

        subjects = [s for s in subjects if s['code'] != subject_code]
        save_subjects(subjects)
        return redirect(url_for('admin_subjects'))

    return render_template('admin_remove_subject.html', subjects=subjects)

@app.route('/admin/set_duration', methods=['GET', 'POST'])
def admin_set_duration():
    """Set attendance session duration"""
    if session.get('user_type') != 'admin':
        return redirect('/')

    current_duration = 120
    try:
        with open('attendance_time.json', 'r') as f:
            current_duration = json.load(f).get('duration', 120)
    except:
        pass

    if request.method == 'POST':
        duration = int(request.form.get('duration', 120))
        try:
            with open('attendance_time.json', 'r') as f:
                data = json.load(f)
        except:
            data = {}
        data['duration'] = duration
        with open('attendance_time.json', 'w') as f:
            json.dump(data, f)
        return redirect(url_for('admin_dashboard', msg=f"Time limit set to {duration} seconds"))

    return render_template('admin_set_duration.html', current_duration=current_duration)

@app.route('/admin/schedule_attendance', methods=['GET', 'POST'])
def admin_schedule_attendance():
    """Schedule attendance"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    subjects = load_subjects()
    
    if request.method == 'POST':
        time_value = request.form.get('time')
        subject = request.form.get('subject', '')
        duration = int(request.form.get('duration', 120))

        if time_value:
            with open('attendance_time.json', 'w') as f:
                json.dump({'time': time_value, 'subject': subject, 'duration': duration}, f)
            return redirect(url_for('admin_dashboard', msg=f"Attendance scheduled for {time_value}"))

    current_time = "15:00"
    current_subject = ""
    current_duration = 120
    try:
        with open('attendance_time.json', 'r') as f:
            data = json.load(f)
            current_time = data.get('time', '15:00')
            current_subject = data.get('subject', '')
            current_duration = data.get('duration', 120)
    except:
        pass

    return render_template('admin_schedule.html',
                         subjects=subjects,
                         current_time=current_time,
                         current_subject=current_subject,
                         current_duration=current_duration)

@app.route('/admin/start_attendance')
def admin_start_attendance():
    """Start manual attendance"""
    if session.get('user_type') != 'admin':
        return redirect('/')

    subject = request.args.get('subject', '')
    duration = 120
    try:
        with open('attendance_time.json', 'r') as f:
            duration = int(json.load(f).get('duration', 120))
    except:
        pass

    return render_template('admin_taking_attendance.html', subject=subject, duration=duration)

# Global variable to store attendance session data
attendance_session = {'marked': set(), 'subject': '', 'active': False}

@app.route('/admin/video_feed')
def admin_video_feed():
    """Video feed for attendance"""
    if session.get('user_type') != 'admin':
        return "Unauthorized", 401
    
    if not FACE_RECOGNITION_ENABLED:
        return "Face recognition disabled", 500
    
    subject = request.args.get('subject', '')
    attendance_session['subject'] = subject
    attendance_session['active'] = True
    attendance_session['marked'] = set()
    
    def generate():
        students = load_students()
        known_encodings = []
        known_usernames = []
        
        for username in students:
            photo_path = os.path.join(DATA_FOLDER, f"{username}.png")
            if os.path.exists(photo_path):
                try:
                    img = face_recognition.load_image_file(photo_path)
                    enc = face_recognition.face_encodings(img)
                    if enc:
                        known_encodings.append(enc[0])
                        known_usernames.append(username)
                except:
                    pass
        
        cap = cv2.VideoCapture(0)
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Read duration from attendance_time.json
        duration = 120
        try:
            with open('attendance_time.json', 'r') as f:
                duration = int(json.load(f).get('duration', 120))
        except:
            pass
        
        start_time = time.time()
        
        try:
            while True:
                if time.time() - start_time > 120:  # 2 minutes timeout
                    break
                
                success, frame = cap.read()
                if not success:
                    break
                
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                locs = face_recognition.face_locations(rgb)
                encs = face_recognition.face_encodings(rgb, locs)
                
                for (top, right, bottom, left), enc in zip(locs, encs):
                    username = "Unknown"
                    name = "Unknown"
                    
                    if known_encodings:
                        distances = face_recognition.face_distance(known_encodings, enc)
                        if len(distances) > 0:
                            min_idx = np.argmin(distances)
                            if distances[min_idx] < 0.6:
                                username = known_usernames[min_idx]
                                name = students[username]['name']
                                
                                if username not in attendance_session['marked']:
                                    attendance_session['marked'].add(username)
                                    print(f"✓ Marked present: {name} ({username})")
                    
                    color = (0, 255, 0) if username != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6), 
                              cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        finally:
            cap.release()
            
            # Save attendance data
            if attendance_session['marked']:
                save_attendance_data(date_str, subject, attendance_session['marked'], students)
            
            attendance_session['active'] = False
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def save_attendance_data(date_str, subject, marked_students, all_students):
    """Save attendance to all storage locations"""
    print(f"\n{'='*60}")
    print(f"Saving attendance for {date_str}")
    print(f"Subject: {subject if subject else 'General'}")
    print(f"Present: {len(marked_students)} students")
    print(f"{'='*60}")
    
    # 1. Save to JSON file
    attendance_file = os.path.join(ATTENDANCE_FOLDER, f"{date_str}.json")
    attendance_data = {
        'date': date_str,
        'subject': subject,
        'present': list(marked_students),
        'absent': [u for u in all_students if u not in marked_students]
    }
    
    with open(attendance_file, 'w') as f:
        json.dump(attendance_data, f, indent=2)
    print(f"✓ Saved to JSON: {attendance_file}")
    
    # 2. Update Excel file
    try:
        update_excel_attendance(date_str, subject, marked_students, all_students)
        print(f"✓ Updated Excel: {EXCEL_FILE_PATH}")
    except Exception as e:
        print(f"✗ Excel update failed: {e}")
    
    # 3. Update Google Sheets
    if SHEETS_ENABLED:
        try:
            update_google_sheets_attendance(date_str, subject, marked_students, all_students)
            print(f"✓ Updated Google Sheets")
        except Exception as e:
            print(f"✗ Google Sheets update failed: {e}")
    else:
        print("⊙ Google Sheets not enabled")
    
    print(f"{'='*60}\n")

def update_google_sheets_attendance(date_str, subject, marked_students, all_students):
    """Update Google Sheets with attendance"""
    if not SHEETS_ENABLED:
        return
    
    try:
        # Get or create sheet
        sheet_name = subject if subject else "General"
        
        try:
            sheet = spreadsheet.worksheet(sheet_name)
        except:
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="50")
        
        # Get existing data
        try:
            all_values = sheet.get_all_values()
            if not all_values or not all_values[0]:
                # Initialize headers
                sheet.update_cell(1, 1, "Name")
                sheet.update_cell(1, 2, "Roll No")
                all_values = [["Name", "Roll No"]]
        except:
            sheet.update_cell(1, 1, "Name")
            sheet.update_cell(1, 2, "Roll No")
            all_values = [["Name", "Roll No"]]
        
        headers = all_values[0] if all_values else ["Name", "Roll No"]
        
        # Add date column if not exists
        if date_str not in headers:
            col_index = len(headers) + 1
            sheet.update_cell(1, col_index, date_str)
            headers.append(date_str)
        else:
            col_index = headers.index(date_str) + 1
        
        # Get existing student rows
        existing_students = {}
        for i, row in enumerate(all_values[1:], start=2):
            if row and len(row) > 0:
                existing_students[row[0]] = i
        
        # Update or add students
        for username, student_data in all_students.items():
            name = student_data['name']
            roll_no = student_data.get('roll_no', '')
            status = "Present" if username in marked_students else "Absent"
            
            if name in existing_students:
                # Update existing row
                row_index = existing_students[name]
                sheet.update_cell(row_index, col_index, status)
            else:
                # Add new row
                row_index = len(all_values) + 1
                sheet.update_cell(row_index, 1, name)
                sheet.update_cell(row_index, 2, roll_no)
                sheet.update_cell(row_index, col_index, status)
                all_values.append([name, roll_no])
        
        print(f"  → Updated {len(marked_students)} present, {len(all_students) - len(marked_students)} absent")
        
    except Exception as e:
        print(f"  → Google Sheets error: {e}")
        raise

@app.route('/admin/stop_attendance', methods=['POST'])
def admin_stop_attendance():
    """Stop attendance session and save data"""
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    if attendance_session['active']:
        date_str = datetime.now().strftime('%Y-%m-%d')
        students = load_students()
        save_attendance_data(date_str, attendance_session['subject'], 
                           attendance_session['marked'], students)
        attendance_session['active'] = False
        
        return jsonify({
            'success': True,
            'marked': len(attendance_session['marked']),
            'total': len(students)
        })
    
    return jsonify({'success': False, 'message': 'No active session'})

@app.route('/admin/view_attendance')
def admin_view_attendance():
    """View attendance records"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    subject = request.args.get('subject', '')
    attendance_data = get_attendance_data(subject)
    subjects = load_subjects()
    
    google_sheet_url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit" if SHEETS_ENABLED else None
    
    return render_template('admin_view_attendance.html',
                         attendance_data=attendance_data,
                         subjects=subjects,
                         selected_subject=subject,
                         google_sheet_url=google_sheet_url)

@app.route('/admin/export_attendance_excel')
def admin_export_attendance_excel():
    """Export attendance to Excel and download"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    subject = request.args.get('subject', '')
    attendance_data = get_attendance_data(subject)
    students = load_students()
    
    try:
        # Build dataframe
        all_dates = sorted(attendance_data.keys())
        rows = []
        for username, student in students.items():
            row = {'Name': student['name'], 'Roll No': student.get('roll_no', '')}
            for date in all_dates:
                data = attendance_data[date]
                row[date] = 'Present' if username in data.get('present', []) else 'Absent'
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        export_path = 'attendance_export.xlsx'
        sheet_name = subject if subject else 'General'
        with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return send_file(
            export_path,
            as_attachment=True,
            download_name=f"attendance_{subject or 'all'}_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return redirect(url_for('admin_view_attendance', subject=subject, msg=f"Export failed: {e}"))

@app.route('/admin/absentees')
def admin_absentees():
    """View today's absentees"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_file = os.path.join(ATTENDANCE_FOLDER, f"{today}.json")
    
    absentees = []
    if os.path.exists(today_file):
        with open(today_file, 'r') as f:
            data = json.load(f)
            absentees = data.get('absent', [])
    
    students = load_students()
    absentee_details = []
    for username in absentees:
        if username in students:
            absentee_details.append({
                'username': username,
                'name': students[username]['name'],
                'roll_no': students[username]['roll_no']
            })
    
    return render_template('admin_absentees.html', absentees=absentee_details, date=today)

@app.route('/admin/shortage')
def admin_shortage():
    """View students with attendance shortage"""
    if session.get('user_type') != 'admin':
        return redirect('/')
    
    students = load_students()
    attendance_data = get_attendance_data()
    
    shortage_list = []
    for username, student in students.items():
        present_count = 0
        total_days = len(attendance_data)
        
        for date, data in attendance_data.items():
            if username in data.get('present', []):
                present_count += 1
        
        if total_days > 0:
            percentage = (present_count / total_days) * 100
            if percentage < 75:
                shortage_list.append({
                    'username': username,
                    'name': student['name'],
                    'roll_no': student['roll_no'],
                    'present': present_count,
                    'total': total_days,
                    'percentage': round(percentage, 2)
                })
    
    return render_template('admin_shortage.html', shortage_list=shortage_list)

# ============================
# Student Routes
# ============================

@app.route('/student/dashboard')
def student_dashboard():
    """Student dashboard"""
    if session.get('user_type') != 'student':
        return redirect('/')
    
    username = session.get('user')
    students = load_students()
    student = students.get(username, {})
    
    # Calculate attendance statistics
    attendance_data = get_attendance_data()
    present_count = 0
    total_days = len(attendance_data)
    
    for date, data in attendance_data.items():
        if username in data.get('present', []):
            present_count += 1
    
    percentage = (present_count / total_days * 100) if total_days > 0 else 0
    
    return render_template('student_dashboard.html',
                         student=student,
                         present_count=present_count,
                         total_days=total_days,
                         percentage=round(percentage, 2))

@app.route('/student/attendance')
def student_attendance():
    """View student's attendance"""
    if session.get('user_type') != 'student':
        return redirect('/')
    
    username = session.get('user')
    subject = request.args.get('subject', '')
    
    attendance_data = get_attendance_data(subject)
    subjects = load_subjects()
    
    my_attendance = []
    for date, data in sorted(attendance_data.items()):
        status = 'Present' if username in data.get('present', []) else 'Absent'
        my_attendance.append({
            'date': date,
            'subject': data.get('subject', 'General'),
            'status': status
        })
    
    return render_template('student_attendance.html',
                         attendance=my_attendance,
                         subjects=subjects,
                         selected_subject=subject)

# ============================
# Utility Routes
# ============================

@app.route('/student_photo/<username>')
def student_photo(username):
    """Serve student photo"""
    photo_path = os.path.join(STUDENT_PHOTOS_FOLDER, f"{username}.png")
    if not os.path.exists(photo_path):
        photo_path = os.path.join(DATA_FOLDER, f"{username}.png")
    
    if os.path.exists(photo_path):
        return send_file(photo_path, mimetype='image/png')
    return "Photo not found", 404

@app.route('/api/marked_count')
def api_marked_count():
    """Return current marked count for live update"""
    if session.get('user_type') != 'admin':
        return jsonify({'count': 0})
    return jsonify({'count': len(attendance_session.get('marked', set()))})

@app.route('/api/check_scheduled')
def api_check_scheduled():
    """Polling endpoint - returns whether scheduled attendance is triggered"""
    if session.get('user_type') != 'admin':
        return jsonify({'triggered': False})
    return jsonify({
        'triggered': scheduled_trigger['active'],
        'subject': scheduled_trigger['subject'],
        'triggered_at': scheduled_trigger['triggered_at']
    })

@app.route('/api/dismiss_scheduled', methods=['POST'])
def api_dismiss_scheduled():
    """Dismiss the scheduled trigger"""
    scheduled_trigger['active'] = False
    scheduled_trigger['subject'] = ''
    scheduled_trigger['triggered_at'] = None
    return jsonify({'success': True})

@app.route('/api/attendance_stats')
def api_attendance_stats():
    """API endpoint for attendance statistics"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    attendance_data = get_attendance_data()
    dates = sorted(attendance_data.keys())
    present_counts = []
    absent_counts = []
    
    for date in dates:
        present_counts.append(len(attendance_data[date].get('present', [])))
        absent_counts.append(len(attendance_data[date].get('absent', [])))
    
    return jsonify({
        'dates': dates,
        'present_counts': present_counts,
        'absent_counts': absent_counts
    })

# ============================
# Run Flask
# ============================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

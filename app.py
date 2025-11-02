from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import subprocess
import gspread
import os, json, base64
from google.oauth2.service_account import Credentials
from datetime import datetime

try:
    import face_recognition
    import cv2
    FACE_RECOGNITION_ENABLED = True
except ImportError:
    FACE_RECOGNITION_ENABLED = False
    print("Face recognition not available. Install opencv-python and face-recognition to enable.")

app = Flask(__name__)

if 'SESSION_SECRET' not in os.environ:
    print("WARNING: SESSION_SECRET not set. Using insecure fallback. Set SESSION_SECRET environment variable for production.")
    app.secret_key = 'dev-secret-key-change-in-production'
else:
    app.secret_key = os.environ['SESSION_SECRET']

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

try:
    creds_b64 = os.environ.get('GOOGLE_CREDS_B64')
    if creds_b64:
        creds_json = base64.b64decode(creds_b64).decode('utf-8')
        credentials = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key('1VAth6jc2rWlUhpSpL7WhrB8ryTiz6d6bd1jgn37i0uE')
        sheet = spreadsheet.worksheet("Attendance")
        SHEETS_ENABLED = True
    else:
        SHEETS_ENABLED = False
        print("Google Sheets credentials not found. Running in demo mode.")
except Exception as e:
    SHEETS_ENABLED = False
    print(f"Google Sheets initialization failed: {e}")

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'bcca')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'bcca')

if ADMIN_USERNAME == 'bcca' and ADMIN_PASSWORD == 'bcca':
    print("WARNING: Using default credentials (bcca/bcca). Set ADMIN_USERNAME and ADMIN_PASSWORD environment variables for security.")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user'] = 'admin'
            return redirect('/dashboard')
        else:
            return render_template('index.html', error='Invalid Credentials')
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    
    msg = request.args.get('msg')
    
    student_count = 0
    if SHEETS_ENABLED:
        try:
            records = sheet.get_all_values()
            student_count = len(records) - 1
        except:
            pass
    else:
        data_files = [f for f in os.listdir('data') if f.endswith('.png')]
        student_count = len(data_files)
    
    return render_template('dashboard.html', msg=msg, student_count=student_count, sheets_enabled=SHEETS_ENABLED, face_recognition_enabled=FACE_RECOGNITION_ENABLED)

@app.route('/view_data')
def view_data():
    if 'user' not in session:
        return redirect('/')
    
    if not SHEETS_ENABLED:
        return render_template('view_data.html', records=[], error="Google Sheets not configured")
    
    try:
        records = sheet.get_all_values()
        return render_template('view_data.html', records=records)
    except Exception as e:
        return render_template('view_data.html', records=[], error=str(e))

@app.route('/shortage')
def shortage():
    if 'user' not in session:
        return redirect('/')
    
    if not SHEETS_ENABLED:
        return render_template('shortage.html', result=[], error="Google Sheets not configured")
    
    try:
        records = sheet.get_all_values()
        if len(records) < 2:
            return render_template('shortage.html', result=[])
        
        headers = records[0][1:]
        result = []
        
        for row in records[1:]:
            if len(row) > 1:
                present_count = row[1:].count('Present')
                total_days = len(headers)
                if total_days > 0 and present_count < total_days * 0.75:
                    percentage = (present_count / total_days * 100) if total_days > 0 else 0
                    result.append({
                        'name': row[0],
                        'present': present_count,
                        'total': total_days,
                        'percentage': round(percentage, 2)
                    })
        
        return render_template('shortage.html', result=result)
    except Exception as e:
        return render_template('shortage.html', result=[], error=str(e))

@app.route('/absentees_today')
def absentees_today():
    if 'user' not in session:
        return redirect('/')
    
    if not SHEETS_ENABLED:
        return render_template('absentees.html', absentees=[], date=datetime.now().strftime('%Y-%m-%d'), error="Google Sheets not configured")
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        records = sheet.get_all_records()
        absentees = [r['Name'] for r in records if r.get(today) == 'Absent']
        return render_template('absentees.html', absentees=absentees, date=today)
    except Exception as e:
        return render_template('absentees.html', absentees=[], date=datetime.now().strftime('%Y-%m-%d'), error=str(e))

@app.route('/run_attendance')
def run_attendance():
    if 'user' not in session:
        return redirect('/')
    
    if not FACE_RECOGNITION_ENABLED:
        return redirect(url_for('dashboard', msg="Face recognition is not available. Install opencv-python and face-recognition first."))
    
    try:
        subprocess.Popen(["uv", "run", "python", "chat.py", "--manual"])
        return redirect(url_for('dashboard', msg="Manual attendance session started! It will run for 2 minutes."))
    except Exception as e:
        return redirect(url_for('dashboard', msg=f"Error starting attendance: {str(e)}"))

@app.route('/set_attendance_time', methods=['GET', 'POST'])
def set_attendance_time():
    if 'user' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        time_value = request.form.get('time')
        if time_value:
            try:
                with open('attendance_time.json', 'w') as f:
                    json.dump({"time": time_value}, f)
                return redirect(url_for('dashboard', msg=f"Attendance time set to {time_value}"))
            except Exception as e:
                return render_template('set_time.html', error=str(e))
    
    current_time = "15:00"
    try:
        with open('attendance_time.json', 'r') as f:
            data = json.load(f)
            current_time = data.get('time', '15:00')
    except:
        pass
    
    return render_template('set_time.html', current_time=current_time)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        photo_data = request.form.get('photo', '')
        
        if not name:
            return render_template('add_student.html', error="Student name is required")
        
        if not photo_data:
            return render_template('add_student.html', error="Photo is required")
        
        try:
            header, encoded = photo_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            
            filename = f"{name}.png"
            os.makedirs("data", exist_ok=True)
            local_path = os.path.join("data", filename)
            
            with open(local_path, "wb") as f:
                f.write(image_bytes)
            
            if FACE_RECOGNITION_ENABLED:
                image = face_recognition.load_image_file(local_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if len(face_encodings) == 0:
                    os.remove(local_path)
                    return render_template('add_student.html', error="No face detected in the photo. Please try again.")
            
            if SHEETS_ENABLED:
                try:
                    existing_data = sheet.get_all_values()
                    new_row = [name] + ['' for _ in range(len(existing_data[0]) - 1)]
                    sheet.append_row(new_row)
                except Exception as e:
                    print(f"Google Sheet append error: {e}")
            
            return redirect(url_for('dashboard', msg=f"Student '{name}' added successfully!"))
            
        except Exception as e:
            return render_template('add_student.html', error=f"Error processing photo: {str(e)}")
    
    return render_template('add_student.html')

@app.route('/remove_student', methods=['GET', 'POST'])
def remove_student():
    if 'user' not in session:
        return redirect('/')
    
    student_names = []
    
    if SHEETS_ENABLED:
        try:
            records = sheet.get_all_values()
            student_names = [row[0] for row in records[1:] if row]
        except:
            pass
    
    data_files = [f.replace('.png', '') for f in os.listdir('data') if f.endswith('.png')]
    student_names = list(set(student_names + data_files))
    student_names.sort()
    
    if request.method == 'POST':
        name_to_remove = request.form.get('name')
        
        if not name_to_remove:
            return render_template('remove_student.html', students=student_names, error="Please select a student")
        
        try:
            photo_path = os.path.join('data', f"{name_to_remove}.png")
            if os.path.exists(photo_path):
                os.remove(photo_path)
            
            if SHEETS_ENABLED:
                try:
                    records = sheet.get_all_values()
                    for idx, row in enumerate(records):
                        if row and row[0] == name_to_remove:
                            sheet.delete_rows(idx + 1)
                            break
                except Exception as e:
                    print(f"Error removing from sheet: {e}")
            
            return redirect(url_for('dashboard', msg=f"Student '{name_to_remove}' removed successfully!"))
        except Exception as e:
            return render_template('remove_student.html', students=student_names, error=str(e))
    
    return render_template('remove_student.html', students=student_names)

@app.route('/students')
def list_students():
    if 'user' not in session:
        return redirect('/')
    
    students = []
    data_files = [f.replace('.png', '') for f in os.listdir('data') if f.endswith('.png')]
    
    for student_name in data_files:
        students.append({
            'name': student_name,
            'photo': f'/student_photo/{student_name}'
        })
    
    return render_template('students.html', students=students)

@app.route('/student_photo/<name>')
def student_photo(name):
    if 'user' not in session:
        return redirect('/')
    
    from flask import send_file
    photo_path = os.path.join('data', f"{name}.png")
    
    if os.path.exists(photo_path):
        return send_file(photo_path, mimetype='image/png')
    else:
        return "Photo not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

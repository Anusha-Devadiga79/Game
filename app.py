from dotenv import load_dotenv
load_dotenv()
import time
from flask import Flask, render_template, request, redirect, session, url_for, send_file
import subprocess, os, json, base64
from datetime import datetime, timedelta
import threading
import pandas as pd

try:
    import face_recognition
    import cv2
    FACE_RECOGNITION_ENABLED = True
except ImportError:
    FACE_RECOGNITION_ENABLED = False
    print("Face recognition not available. Install opencv-python and face-recognition to enable.")

# Flask App
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Session key
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
GOOGLE_SHEET_ID = '1VAth6jc2rWlUhpSpL7WhrB8ryTiz6d6bd1jgn37i0uE'
EXCEL_FILE_PATH = os.path.join(os.getcwd(), 'attendance_backup.xlsx')

try:
    import gspread
    from google.oauth2.service_account import Credentials
    creds_b64 = os.environ.get('GOOGLE_CREDS_B64')
    if creds_b64:
        creds_json = base64.b64decode(creds_b64).decode('utf-8')
        credentials = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(GOOGLE_SHEET_ID)
        sheet = spreadsheet.worksheet("Attendance")
        SHEETS_ENABLED = True
    else:
        SHEETS_ENABLED = False
        print("Google Sheets credentials not found. Running in demo mode.")
except Exception as e:
    SHEETS_ENABLED = False
    print(f"Google Sheets initialization failed: {e}")

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME','bcca')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD','bcca')

# ============================
# Background Scheduler Thread
# ============================
def schedule_attendance():
    while True:
        try:
            with open('attendance_time.json','r') as f:
                data = json.load(f)
                time_str = data.get('time')
                if time_str:
                    now = datetime.now()
                    schedule_time = datetime.strptime(time_str,'%H:%M').replace(year=now.year, month=now.month, day=now.day)
                    if now >= schedule_time and now < schedule_time + timedelta(minutes=1):
                        print("Running scheduled attendance...")
                        subprocess.Popen(["python","chat.py"], shell=False)
                        time.sleep(60)
        except Exception:
            pass
        time.sleep(10)

threading.Thread(target=schedule_attendance,daemon=True).start()

# ============================
# Routes
# ============================

@app.route('/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username = request.form.get('username','')
        password = request.form.get('password','')
        if username==ADMIN_USERNAME and password==ADMIN_PASSWORD:
            session['user']='admin'
            return redirect('/dashboard')
        else:
            return render_template('index.html',error="Invalid Credentials")
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/')
    msg = request.args.get('msg')
    # Count students
    student_count = 0
    if SHEETS_ENABLED:
        try:
            records = sheet.get_all_values()
            student_count = len(records)-1
        except: pass
    else:
        if os.path.exists(EXCEL_FILE_PATH):
            df = pd.read_excel(EXCEL_FILE_PATH)
            student_count = len(df)
        else:
            student_count = len([f for f in os.listdir('data') if f.endswith('.png')])
    return render_template('dashboard.html', msg=msg, student_count=student_count,
                           sheets_enabled=SHEETS_ENABLED, face_recognition_enabled=FACE_RECOGNITION_ENABLED)

@app.route('/set_attendance_time',methods=['GET','POST'])
def set_attendance_time():
    if 'user' not in session: return redirect('/')
    if request.method=='POST':
        time_value = request.form.get('time')
        if time_value:
            try:
                with open('attendance_time.json','w') as f:
                    json.dump({"time":time_value},f)
                return redirect(url_for('dashboard', msg=f"Attendance time set to {time_value}"))
            except Exception as e:
                return render_template('set_time.html', error=str(e))
    current_time = "15:00"
    try:
        with open('attendance_time.json','r') as f:
            data = json.load(f)
            current_time = data.get('time','15:00')
    except: pass
    return render_template('set_time.html',current_time=current_time)

@app.route('/run_attendance')
def run_attendance():
    if 'user' not in session: return redirect('/')
    if not FACE_RECOGNITION_ENABLED:
        return redirect(url_for('dashboard', msg="Face recognition not available"))
    try:
        subprocess.Popen(["python","chat.py","--manual"], shell=False)
        return redirect(url_for('dashboard', msg="Manual attendance started!"))
    except Exception as e:
        return redirect(url_for('dashboard', msg=f"Error: {str(e)}"))

# ----------------------------
# Add / Remove / List students
# ----------------------------
@app.route('/add_student',methods=['GET','POST'])
def add_student():
    if 'user' not in session: return redirect('/')
    if request.method=='POST':
        name = request.form.get('name','').strip()
        photo_data = request.form.get('photo','')
        if not name: return render_template('add_student.html',error="Student name required")
        if not photo_data: return render_template('add_student.html',error="Photo required")
        try:
            header,encoded = photo_data.split(',',1)
            image_bytes = base64.b64decode(encoded)
            os.makedirs("data",exist_ok=True)
            local_path = os.path.join("data",f"{name}.png")
            with open(local_path,'wb') as f: f.write(image_bytes)
            if FACE_RECOGNITION_ENABLED:
                image = face_recognition.load_image_file(local_path)
                face_encodings = face_recognition.face_encodings(image)
                if len(face_encodings)==0:
                    os.remove(local_path)
                    return render_template('add_student.html',error="No face detected")
            if SHEETS_ENABLED:
                try:
                    existing_data = sheet.get_all_values()
                    new_row = [name]+['' for _ in range(len(existing_data[0])-1)]
                    sheet.append_row(new_row)
                except: pass
            else:
                if os.path.exists(EXCEL_FILE_PATH):
                    df = pd.read_excel(EXCEL_FILE_PATH)
                    df.loc[len(df)] = [name]
                    df.to_excel(EXCEL_FILE_PATH,index=False)
                else:
                    pd.DataFrame([[name]],columns=["Name"]).to_excel(EXCEL_FILE_PATH,index=False)
            return redirect(url_for('dashboard',msg=f"Student '{name}' added!"))
        except Exception as e:
            return render_template('add_student.html',error=str(e))
    return render_template('add_student.html')

@app.route('/remove_student',methods=['GET','POST'])
def remove_student():
    if 'user' not in session: return redirect('/')
    student_names = []
    if SHEETS_ENABLED:
        try:
            records = sheet.get_all_values()
            student_names = [r[0] for r in records[1:] if r]
        except: pass
    data_files = [f.replace('.png','') for f in os.listdir('data') if f.endswith('.png')]
    student_names = list(set(student_names+data_files))
    student_names.sort()
    if request.method=='POST':
        name_to_remove = request.form.get('name')
        if not name_to_remove: return render_template('remove_student.html',students=student_names,error="Select student")
        try:
            photo_path = os.path.join('data',f"{name_to_remove}.png")
            if os.path.exists(photo_path): os.remove(photo_path)
            if SHEETS_ENABLED:
                try:
                    records = sheet.get_all_values()
                    for idx,row in enumerate(records):
                        if row and row[0]==name_to_remove:
                            sheet.delete_rows(idx+1)
                            break
                except: pass
            else:
                if os.path.exists(EXCEL_FILE_PATH):
                    df = pd.read_excel(EXCEL_FILE_PATH)
                    df = df[df['Name']!=name_to_remove]
                    df.to_excel(EXCEL_FILE_PATH,index=False)
            return redirect(url_for('dashboard',msg=f"Student '{name_to_remove}' removed!"))
        except Exception as e:
            return render_template('remove_student.html',students=student_names,error=str(e))
    return render_template('remove_student.html',students=student_names)

@app.route('/students')
def list_students():
    if 'user' not in session: return redirect('/')
    students = [{'name':f.replace('.png',''),'photo':f"/student_photo/{f.replace('.png','')}"}
                for f in os.listdir('data') if f.endswith('.png')]
    return render_template('students.html',students=students)

@app.route('/student_photo/<name>')
def student_photo(name):
    if 'user' not in session: return redirect('/')
    photo_path = os.path.join('data',f"{name}.png")
    if os.path.exists(photo_path): return send_file(photo_path,mimetype='image/png')
    return "Photo not found",404

# ----------------------------
# Additional missing routes
# ----------------------------
@app.route('/view_data')
def view_data():
    if 'user' not in session: return redirect('/')
    records = []
    if SHEETS_ENABLED:
        try:
            records = sheet.get_all_values()
        except: pass
    elif os.path.exists(EXCEL_FILE_PATH):
        df = pd.read_excel(EXCEL_FILE_PATH)
        records = [df.columns.tolist()] + df.values.tolist()
    return render_template('view_data.html',records=records)

@app.route('/absentees_today')
def absentees_today():
    if 'user' not in session: return redirect('/')
    absentees = []
    today = datetime.now().strftime('%Y-%m-%d')
    if SHEETS_ENABLED:
        try:
            records = sheet.get_all_records()
            absentees = [r['Name'] for r in records if r.get(today)=='Absent']
        except: pass
    return render_template('absentees.html',absentees=absentees,date=today)

@app.route('/shortage')
def shortage():
    if 'user' not in session: return redirect('/')
    result = []
    if SHEETS_ENABLED:
        try:
            records = sheet.get_all_values()
            headers = records[0][1:] if len(records)>0 else []
            for row in records[1:]:
                if len(row) > 1:
                    present_count = row[1:].count('Present')
                    total_days = len(headers)
                    if total_days>0 and present_count < total_days*0.75:
                        percentage = (present_count/total_days)*100
                        result.append({'name':row[0],'present':present_count,'total':total_days,'percentage':round(percentage,2)})
        except: pass
    return render_template('shortage.html',result=result)

# ============================
# Run Flask
# ============================
if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)

import face_recognition
import cv2
import numpy as np
from datetime import datetime, time as dt_time
import time
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import sys
import base64

manual_mode = "--manual" in sys.argv or os.environ.get("MANUAL_RUN") == "1"

try:
    with open("attendance_time.json", "r") as f:
        data = json.load(f)
        hour, minute = map(int, data["time"].split(":"))
        START_TIME = dt_time(hour=hour, minute=minute)
except:
    START_TIME = dt_time(hour=15, minute=0)

print(f"Attendance scheduled for: {START_TIME.strftime('%H:%M')}")

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

image_paths = {}
for filename in os.listdir(DATA_FOLDER):
    if filename.endswith('.png') or filename.endswith('.jpg'):
        name = os.path.splitext(filename)[0]
        image_paths[name] = os.path.join(DATA_FOLDER, filename)

print(f"Loaded {len(image_paths)} student images from data folder")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

try:
    creds_b64 = os.environ.get('GOOGLE_CREDS_B64')
    if creds_b64:
        creds_json = base64.b64decode(creds_b64).decode('utf-8')
        credentials = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
        gc = gspread.authorize(credentials)
        SPREADSHEET_ID = "1VAth6jc2rWlUhpSpL7WhrB8ryTiz6d6bd1jgn37i0uE"
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        SHEETS_ENABLED = True
        print("Google Sheets connected successfully")
    else:
        SHEETS_ENABLED = False
        print("Google Sheets credentials not found. Attendance will only be saved locally.")
except Exception as e:
    SHEETS_ENABLED = False
    print(f"Google Sheets initialization failed: {e}")

known_face_encodings = []
known_face_names = []

for name, path in image_paths.items():
    try:
        image = face_recognition.load_image_file(path)
        face_encoding = face_recognition.face_encodings(image)
        if len(face_encoding) > 0:
            known_face_encodings.append(face_encoding[0])
            known_face_names.append(name)
            print(f"Loaded face encoding for: {name}")
        else:
            print(f"No face found in image: {name}")
    except Exception as e:
        print(f"Error loading image for {name}: {e}")

print(f"Total faces loaded: {len(known_face_names)}")

def update_google_sheet(sheet, date_header, name):
    if not SHEETS_ENABLED:
        return
    
    try:
        headers = sheet.row_values(1)
        if not headers or headers[0] != "Name":
            sheet.update_cell(1, 1, "Name")
            headers = ["Name"]
        
        row_values = sheet.col_values(1)
        if len(row_values) == 1:
            for i, student in enumerate(known_face_names, start=2):
                sheet.update_cell(i, 1, student)
        
        row_values = sheet.col_values(1)
        if date_header not in headers:
            sheet.update_cell(1, len(headers) + 1, date_header)
            headers.append(date_header)
        
        col_index = headers.index(date_header) + 1
        
        for student in known_face_names:
            row_index = row_values.index(student) + 1 if student in row_values else len(row_values) + 1
            if student == name:
                sheet.update_cell(row_index, col_index, "Present")
            elif not sheet.cell(row_index, col_index).value:
                sheet.update_cell(row_index, col_index, "Absent")
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")

def save_attendance_locally(date_header, attendance_dict):
    os.makedirs("attendance_logs", exist_ok=True)
    log_file = os.path.join("attendance_logs", f"{date_header}.json")
    
    with open(log_file, 'w') as f:
        json.dump(attendance_dict, f, indent=2)
    
    print(f"Attendance saved locally to {log_file}")

def take_attendance(duration=120):
    print("Taking Attendance...")
    date_header = datetime.now().strftime("%Y-%m-%d")
    
    if len(known_face_encodings) == 0:
        print("No student faces loaded. Please add students first.")
        return
    
    if SHEETS_ENABLED:
        try:
            worksheets = spreadsheet.worksheets()
            sheet_titles = [ws.title for ws in worksheets]
            if "Attendance" not in sheet_titles:
                spreadsheet.add_worksheet(title="Attendance", rows="100", cols="10")
            sheet = spreadsheet.worksheet("Attendance")
        except Exception as e:
            print(f"Error accessing Google Sheet: {e}")
            sheet = None
    else:
        sheet = None
    
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Camera failed to open. Please check camera permissions.")
        return
    
    already_marked = set()
    start_time = time.time()
    
    print("Camera opened. Press 'q' to quit early.")
    
    while True:
        ret, frame = capture.read()
        if not ret:
            print("Camera frame error.")
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if len(distances) > 0:
                min_distance_index = np.argmin(distances)
                if distances[min_distance_index] < 0.6:
                    name = known_face_names[min_distance_index]
            
            if name != "Unknown" and name not in already_marked:
                print(f"Recognized: {name}")
                already_marked.add(name)
                if sheet:
                    update_google_sheet(sheet, date_header, name)
            
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.7, (255, 255, 255), 1)
        
        cv2.imshow("Attendance System - Press 'q' to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        if manual_mode and time.time() - start_time > duration:
            print("Time limit reached.")
            break
    
    capture.release()
    cv2.destroyAllWindows()
    
    attendance_dict = {
        "date": date_header,
        "present": list(already_marked),
        "absent": [name for name in known_face_names if name not in already_marked]
    }
    save_attendance_locally(date_header, attendance_dict)
    
    print(f"Attendance session ended. {len(already_marked)} students marked present.")

if not manual_mode:
    start_wait = time.time()
    print(f"Waiting for scheduled time: {START_TIME.strftime('%H:%M')}")
    while True:
        current_time = datetime.now().time()
        if current_time.hour == START_TIME.hour and current_time.minute == START_TIME.minute:
            print("Starting scheduled attendance...")
            take_attendance()
            break
        if time.time() - start_wait > 120:
            print("Attendance time limit reached. Exiting...")
            break
        time.sleep(10)
else:
    take_attendance(duration=120)

"""
Attendance Runner Script
Runs face recognition attendance system
"""
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import time
import os
import json
import sys

# Get subject from command line
subject = sys.argv[1] if len(sys.argv) > 1 else ''

# Paths
DATA_FOLDER = 'data'
STUDENT_DATA_FILE = 'students_data.json'
ATTENDANCE_FOLDER = 'attendance_logs'
EXCEL_FILE_PATH = 'attendance_backup.xlsx'

os.makedirs(ATTENDANCE_FOLDER, exist_ok=True)

# Load students
students = {}
if os.path.exists(STUDENT_DATA_FILE):
    with open(STUDENT_DATA_FILE, 'r') as f:
        students = json.load(f)

# Load face encodings
known_encodings = []
known_usernames = []

print(f"Loading student faces from {DATA_FOLDER}...")
for username in students:
    photo_path = os.path.join(DATA_FOLDER, f"{username}.png")
    if os.path.exists(photo_path):
        try:
            img = face_recognition.load_image_file(photo_path)
            enc = face_recognition.face_encodings(img)
            if enc:
                known_encodings.append(enc[0])
                known_usernames.append(username)
                print(f"Loaded: {students[username]['name']}")
        except Exception as e:
            print(f"Error loading {username}: {e}")

print(f"\nTotal faces loaded: {len(known_usernames)}")

if len(known_encodings) == 0:
    print("No student faces found. Exiting...")
    sys.exit(1)

# Start camera
print("\nStarting camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Failed to open camera!")
    sys.exit(1)

date_str = datetime.now().strftime('%Y-%m-%d')
marked_today = set()
start_time = time.time()
duration = 120  # 2 minutes

print(f"\nAttendance session started for {subject if subject else 'General'}")
print("Press 'q' to quit early\n")

while True:
    # Check timeout
    if time.time() - start_time > duration:
        print("\nTime limit reached!")
        break
    
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break
    
    # Detect faces
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)
    
    # Process each face
    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
        username = "Unknown"
        name = "Unknown"
        
        if known_encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)
            if len(distances) > 0:
                min_idx = np.argmin(distances)
                if distances[min_idx] < 0.6:
                    username = known_usernames[min_idx]
                    name = students[username]['name']
                    
                    if username not in marked_today:
                        marked_today.add(username)
                        print(f"✓ Marked present: {name} ({username})")
        
        # Draw rectangle
        color = (0, 255, 0) if username != "Unknown" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
    
    # Show frame
    cv2.imshow('Attendance System - Press q to quit', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\nManually stopped")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

# Save attendance
attendance_file = os.path.join(ATTENDANCE_FOLDER, f"{date_str}.json")
attendance_data = {
    'date': date_str,
    'subject': subject,
    'present': list(marked_today),
    'absent': [u for u in students if u not in marked_today]
}

with open(attendance_file, 'w') as f:
    json.dump(attendance_data, f, indent=2)

print(f"\n{'='*50}")
print(f"Attendance Summary for {date_str}")
print(f"Subject: {subject if subject else 'General'}")
print(f"Present: {len(marked_today)}")
print(f"Absent: {len(students) - len(marked_today)}")
print(f"{'='*50}")
print(f"\nAttendance saved to {attendance_file}")

# Update Excel
try:
    import pandas as pd
    from openpyxl import load_workbook
    
    if os.path.exists(EXCEL_FILE_PATH):
        df_dict = pd.read_excel(EXCEL_FILE_PATH, sheet_name=None)
    else:
        df_dict = {}
    
    sheet_name = subject if subject else "General"
    
    if sheet_name not in df_dict:
        df_dict[sheet_name] = pd.DataFrame(columns=['Name', 'Roll No'])
    
    sheet_df = df_dict[sheet_name]
    
    if date_str not in sheet_df.columns:
        sheet_df[date_str] = 'Absent'
    
    for username in students:
        student = students[username]
        if student['name'] not in sheet_df['Name'].values:
            new_row = pd.DataFrame([[student['name'], student['roll_no']]], 
                                 columns=['Name', 'Roll No'])
            sheet_df = pd.concat([sheet_df, new_row], ignore_index=True)
    
    for username in marked_today:
        student = students[username]
        sheet_df.loc[sheet_df['Name'] == student['name'], date_str] = 'Present'
    
    df_dict[sheet_name] = sheet_df
    
    with pd.ExcelWriter(EXCEL_FILE_PATH, engine='openpyxl') as writer:
        for sheet, data in df_dict.items():
            data.to_excel(writer, sheet_name=sheet, index=False)
    
    print(f"Excel file updated: {EXCEL_FILE_PATH}")
except Exception as e:
    print(f"Excel update failed: {e}")

print("\nAttendance session completed!")

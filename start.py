"""
Quick Start Script for Smart Attendance System
Creates initial data files and starts the application
"""
import os
import json

print("=" * 60)
print("🎓 Smart Attendance System - Setup")
print("=" * 60)

# Create necessary directories
directories = [
    'attendance_logs',
    'student_photos',
    'data',
    'static/css',
    'static/js',
    'templates'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"✓ Created directory: {directory}")

# Create initial data files
if not os.path.exists('students_data.json'):
    with open('students_data.json', 'w') as f:
        json.dump({}, f, indent=2)
    print("✓ Created students_data.json")

if not os.path.exists('subjects.json'):
    with open('subjects.json', 'w') as f:
        json.dump([], f, indent=2)
    print("✓ Created subjects.json")

if not os.path.exists('attendance_time.json'):
    with open('attendance_time.json', 'w') as f:
        json.dump({"time": "15:00", "subject": ""}, f, indent=2)
    print("✓ Created attendance_time.json")

if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write("""# Admin Credentials
ADMIN_USERNAME=bcca
ADMIN_PASSWORD=bcca

# Session Secret (Change in production!)
SESSION_SECRET=dev-secret-key-change-in-production

# Google Sheets (Optional - Leave empty if not using)
GOOGLE_CREDS_B64=
GOOGLE_SHEET_ID=
GOOGLE_DRIVE_FOLDER_ID=
""")
    print("✓ Created .env file")

print("\n" + "=" * 60)
print("Setup Complete! 🎉")
print("=" * 60)
print("\nDefault Admin Credentials:")
print("  Username: bcca")
print("  Password: bcca")
print("\nStarting application...")
print("Access at: http://localhost:5000")
print("=" * 60 + "\n")

# Start the application
import subprocess
subprocess.run(["python", "app_enhanced.py"])

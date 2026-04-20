# 🎓 Smart Attendance System - Professional Edition

A comprehensive face recognition-based attendance system with separate admin and student portals, subject-wise tracking, and detailed analytics.

## ✨ Features

### Admin Portal
- **Dashboard with Statistics**
  - Total students count
  - Total subjects
  - Today's attendance
  - System status indicators
  - Attendance trend graphs

- **Attendance Control**
  - Start attendance now (manual)
  - Schedule attendance for specific time
  - Subject-wise attendance tracking
  - Live camera feed with face recognition
  - Automatic marking (2-minute session)

- **Student Management**
  - Add students with complete details (Name, Roll No, Class, Semester, Password)
  - Live camera capture for student photos
  - Face verification during registration
  - View all students with photos
  - Remove students

- **Subject Management**
  - Add subjects with code and name
  - View all subjects
  - Subject-wise attendance tracking

- **Reports & Analytics**
  - View attendance records (date-wise, subject-wise)
  - Today's absentees list
  - Shortage report (students below 75%)
  - Attendance trend visualization

### Student Portal
- **Personal Dashboard**
  - Profile information
  - Attendance percentage with visual indicator
  - Present/Absent days count
  - Shortage alert (if below 75%)

- **Attendance Records**
  - View complete attendance history
  - Filter by subject
  - Date-wise attendance status

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install System Dependencies (for face_recognition)

**Windows:**
- Install CMake: https://cmake.org/download/
- Install Visual Studio Build Tools
- Install dlib: `pip install dlib`

**Linux:**
```bash
sudo apt-get update
sudo apt-get install cmake
sudo apt-get install python3-dev
```

**macOS:**
```bash
brew install cmake
```

### 3. Configure Environment Variables

Create a `.env` file:

```env
# Admin Credentials
ADMIN_USERNAME=bcca
ADMIN_PASSWORD=bcca

# Session Secret
SESSION_SECRET=your-secret-key-here

# Google Sheets (Optional)
GOOGLE_CREDS_B64=your-base64-encoded-credentials
GOOGLE_SHEET_ID=your-sheet-id
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
```

### 4. Google Sheets Setup (Optional)

1. Create a Google Cloud Project
2. Enable Google Sheets API and Google Drive API
3. Create a Service Account
4. Download credentials JSON
5. Convert to base64: `base64 credentials.json`
6. Add to `.env` as `GOOGLE_CREDS_B64`

## 📖 Usage

### Starting the Application

```bash
python app_enhanced.py
```

Access at: `http://localhost:5000`

### Default Login Credentials

**Admin:**
- Username: `bcca`
- Password: `bcca`

**Students:**
- Username: (set during registration)
- Password: (set during registration)

## 🎯 Workflow

### For Administrators

1. **Login** as admin (bcca/bcca)

2. **Add Subjects**
   - Go to Subject Management tab
   - Click "Add Subject"
   - Enter subject code and name
   - Example: CS101 - Data Structures

3. **Add Students**
   - Go to Student Management tab
   - Click "Add Student"
   - Fill in details:
     - Username (for login)
     - Full Name
     - Roll Number
     - Class (e.g., BCA, MCA)
     - Semester (1-6)
     - Password (for student login)
   - Click "Open Camera"
   - Position face in camera
   - Click "Capture Photo"
   - Submit form

4. **Take Attendance**

   **Option A: Manual (Immediate)**
   - Go to Attendance Control tab
   - Click "Start Attendance Now"
   - Select subject (optional)
   - Camera opens for 2 minutes
   - Students appear in front of camera
   - System automatically marks present
   - Green box = Recognized
   - Red box = Unknown

   **Option B: Scheduled (Automatic)**
   - Go to Attendance Control tab
   - Click "Schedule Attendance"
   - Set time (e.g., 15:00)
   - Select subject
   - System automatically runs at scheduled time

5. **View Reports**
   - View Attendance: See all attendance records
   - Today's Absentees: See who's absent today
   - Shortage Report: See students below 75%

### For Students

1. **Login** with your username and password

2. **View Dashboard**
   - See your attendance percentage
   - Check present/absent days
   - View shortage alerts

3. **View Attendance**
   - See complete attendance history
   - Filter by subject
   - Check date-wise status

## 📊 Data Storage

### Local Storage
- **students_data.json**: Student information
- **subjects.json**: Subject list
- **attendance_logs/**: Daily attendance records
- **student_photos/**: Student photos
- **data/**: Face recognition data
- **attendance_backup.xlsx**: Excel backup (subject-wise sheets)

### Google Sheets (Optional)
- Attendance synced to Google Sheets
- Photos uploaded to Google Drive
- Real-time backup

## 🔧 Configuration

### Attendance Duration
Edit `attendance_runner.py`:
```python
duration = 120  # Change to desired seconds
```

### Face Recognition Threshold
Edit `attendance_runner.py`:
```python
if distances[min_idx] < 0.6:  # Lower = stricter
```

### Minimum Attendance Percentage
Edit templates to change 75% threshold

## 🎨 Customization

### Colors
Edit inline styles in templates or create `static/css/custom.css`

### Logo
Add your logo to navbar in templates

### Additional Fields
Modify `students_data.json` structure and forms

## 🐛 Troubleshooting

### Camera Not Opening
- Check camera permissions
- Ensure no other app is using camera
- Try different camera index: `cv2.VideoCapture(1)`

### Face Not Detected
- Ensure good lighting
- Face camera directly
- Remove glasses/masks if possible
- Adjust threshold in code

### Google Sheets Not Working
- Verify credentials are correct
- Check API is enabled
- Ensure service account has access to sheet

### Excel File Errors
- Install openpyxl: `pip install openpyxl`
- Check file permissions
- Close Excel if file is open

## 📱 Mobile Access

The interface is responsive and works on mobile browsers. Students can check attendance from phones.

## 🔒 Security

- Passwords stored in plain text (for demo)
- For production: Use `werkzeug.security` for hashing
- Add HTTPS in production
- Implement rate limiting
- Add CSRF protection

## 🚀 Production Deployment

1. Change default admin password
2. Set strong SESSION_SECRET
3. Enable HTTPS
4. Use production WSGI server (gunicorn)
5. Set up proper database (PostgreSQL/MySQL)
6. Implement password hashing
7. Add backup system
8. Set up monitoring

## 📝 Future Enhancements

- Email notifications for shortage
- SMS alerts for absentees
- Biometric integration
- Mobile app
- QR code attendance
- Geolocation verification
- Multiple camera support
- Batch photo upload
- Report export (PDF)
- Parent portal

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review error logs
3. Verify all dependencies installed
4. Check camera and permissions

## 📄 License

This project is for educational purposes.

## 🎉 Credits

Built with:
- Flask (Web Framework)
- face_recognition (Face Recognition)
- OpenCV (Computer Vision)
- Google Sheets API (Cloud Storage)
- Chart.js (Visualizations)

---

**Note**: This is an enhanced version with professional UI and complete features. The original `app.py` is preserved for reference.

## Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app_enhanced.py

# Run manual attendance (alternative)
python attendance_runner.py

# Run scheduled attendance with subject
python attendance_runner.py CS101
```

## File Structure

```
├── app_enhanced.py              # Main Flask application
├── attendance_runner.py         # Attendance script
├── requirements.txt             # Dependencies
├── students_data.json          # Student database
├── subjects.json               # Subjects list
├── attendance_time.json        # Schedule config
├── attendance_logs/            # Daily attendance
├── student_photos/             # Student photos
├── data/                       # Face encodings
├── templates/                  # HTML templates
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── admin_add_student.html
│   ├── admin_taking_attendance.html
│   ├── student_dashboard.html
│   └── ... (other templates)
└── static/
    └── css/
        └── style.css
```

Enjoy your Smart Attendance System! 🎓✨

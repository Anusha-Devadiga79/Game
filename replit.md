# Smart Attendance System

A Flask-based face recognition attendance system with comprehensive admin dashboard, student management, and attendance reporting capabilities.

## Overview

This project is a web application that uses face recognition technology to automatically track student attendance. The system provides:

- **Authentication**: Secure admin login system
- **Student Management**: Add, remove, and view registered students with photos
- **Attendance Tracking**: Automated face recognition-based attendance capture
- **Reports & Analytics**: View attendance data, absentees, and shortage reports
- **Cloud Integration**: Optional Google Sheets sync for attendance records

## Project Structure

```
.
├── app.py                 # Main Flask application with all routes
├── chat.py               # Attendance capture script with face recognition
├── camera.py             # Simple camera capture utility
├── attendance_time.json  # Configuration for scheduled attendance
├── data/                 # Student photos storage
├── templates/            # HTML templates
│   ├── index.html       # Login page
│   ├── dashboard.html   # Main dashboard
│   ├── add_student.html # Add student with webcam
│   ├── remove_student.html
│   ├── view_data.html   # Attendance records
│   ├── absentees.html   # Today's absentees
│   ├── shortage.html    # Students below 75% attendance
│   ├── set_time.html    # Configure attendance schedule
│   └── students.html    # View all students
└── static/
    └── css/
        └── style.css    # Modern, responsive styling
```

## Features

### Current State (November 2, 2025)

#### Working Features:
- ✅ User authentication (username: bcca, password: bcca)
- ✅ Modern, responsive UI with gradient design
- ✅ Student management (add/remove students)
- ✅ Webcam photo capture for student registration
- ✅ Attendance data viewing
- ✅ Absentees and shortage reports
- ✅ Attendance scheduling configuration

#### Optional Features (Require Setup):
- Face Recognition: Requires installing `opencv-python` and `face-recognition` packages
- Google Sheets Integration: Requires setting up `GOOGLE_CREDS_B64` environment variable

## Setup Instructions

### 1. Dependencies

All Python packages are already configured in `pyproject.toml`:
- Flask (web framework)
- gspread (Google Sheets API)
- google-auth (authentication)
- google-api-python-client (Drive API)
- openpyxl (Excel handling)
- numpy (numerical operations)
- werkzeug (utilities)

**Optional packages for face recognition:**
```bash
uv pip install opencv-python face-recognition
```

Note: Face recognition requires system dependencies (CMake, gcc) which are already installed.

### 2. Environment Variables

#### Recommended:
- `SESSION_SECRET`: Flask session secret (uses secure fallback with warning if not set)
- `ADMIN_USERNAME`: Admin username (defaults to 'bcca')
- `ADMIN_PASSWORD`: Admin password (defaults to 'bcca')

**Security Note**: Always set these environment variables in production. The default values are only suitable for development/testing.

#### Optional:
- `GOOGLE_CREDS_B64`: Base64-encoded Google service account credentials for Sheets integration

To enable Google Sheets sync:
1. Create a Google Cloud service account
2. Download the JSON credentials
3. Base64 encode: `cat credentials.json | base64 -w 0`
4. Add as environment secret: `GOOGLE_CREDS_B64`

### 3. Login Credentials

Default credentials (development only):
- Username: `bcca`
- Password: `bcca`

**Production Setup**: 
1. Set `ADMIN_USERNAME` environment variable to your desired username
2. Set `ADMIN_PASSWORD` environment variable to your desired password
3. The app will warn on startup if default credentials are in use

## Usage

### Manual Attendance

1. Log in to the dashboard
2. Click "Start Attendance Now"
3. The system will open a camera window for 2 minutes
4. Students' faces will be recognized and marked present automatically

### Scheduled Attendance

1. Go to "Set Schedule" in the dashboard
2. Choose the time for automatic attendance
3. Run `uv run python chat.py` separately (not from web interface) at the scheduled time

### Student Management

**Add Student:**
1. Navigate to "Add Student"
2. Enter student name
3. Click "Capture Photo" to take a webcam photo
4. Submit to register

**Remove Student:**
1. Navigate to "Remove Student"
2. Select student from dropdown
3. Confirm deletion

### Reports

- **View Attendance**: See complete attendance records in table format
- **Today's Absentees**: Quick view of students absent today
- **Shortage Report**: Students below 75% attendance threshold

## Technical Details

### Architecture

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: Google Sheets (optional) + local file storage
- **Face Recognition**: OpenCV + face_recognition library

### Security

- Session-based authentication
- File size limits (16MB max)
- Input validation on all forms
- Secure file handling

### Responsive Design

The UI is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile devices

## Recent Changes

**November 2, 2025:**
- Created complete Flask web application with modern UI
- Implemented all student management routes
- Built responsive templates with gradient design
- Made face recognition optional (graceful degradation)
- Added Google Sheets integration with fallback to local storage
- Configured workflow to run on port 5000

## User Preferences

- Clean, modern UI with gradient backgrounds
- All major features accessible from dashboard
- Real-time camera preview for student registration
- Clear status messages and error handling

## Known Limitations

1. Face recognition packages (opencv-python, face-recognition) are optional
2. Installation of face recognition may take time due to dlib compilation
3. Google Sheets integration requires manual credential setup
4. Camera access requires HTTPS or localhost

## Future Enhancements

- Add student photo gallery with profile management
- Implement attendance statistics dashboard with charts
- Create CSV/Excel export functionality
- Add email notifications for shortage alerts
- Implement date range filtering and search
- Add bulk student import feature
- Implement role-based access control

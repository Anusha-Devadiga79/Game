# 📖 Smart Attendance System - Complete Usage Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Install & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script
python start.py
```

### Step 2: Access Application
- Open browser: `http://localhost:5000`
- Login as Admin: `bcca` / `bcca`

### Step 3: Add Students & Take Attendance
- Add subjects → Add students → Start attendance!

---

## 📋 Detailed Walkthrough

### 1️⃣ ADMIN SETUP

#### A. Login
1. Go to `http://localhost:5000`
2. Select "Admin" tab
3. Username: `bcca`
4. Password: `bcca`
5. Click "Login"

#### B. Add Subjects First
1. Click "Subject Management" tab
2. Click "Add Subject"
3. Fill in:
   - Subject Code: `CS101`
   - Subject Name: `Data Structures`
4. Click "Add Subject"
5. Repeat for all subjects

**Example Subjects:**
- CS101 - Data Structures
- CS102 - Database Management
- CS103 - Web Development
- MATH201 - Discrete Mathematics

#### C. Add Students
1. Click "Student Management" tab
2. Click "Add Student"
3. Fill in ALL fields:
   - **Username**: `john_doe` (for login)
   - **Full Name**: `John Doe`
   - **Roll Number**: `BCA001`
   - **Class**: `BCA`
   - **Semester**: `3`
   - **Password**: `student123`

4. **Capture Photo:**
   - Click "Open Camera"
   - Position face in center
   - Ensure good lighting
   - Face camera directly
   - Click "Capture Photo"
   - Preview appears below
   - If not good, click "Retake"

5. Click "Add Student"
6. Success message appears
7. Repeat for all students

**Important Notes:**
- Photo MUST show clear face
- Good lighting is essential
- Remove glasses/masks if possible
- Face must be detected (green box)
- Username must be unique

### 2️⃣ TAKING ATTENDANCE

#### Method A: Manual (Immediate)

1. Go to "Attendance Control" tab
2. Click "Start Attendance Now"
3. Camera opens automatically
4. **2-minute session starts**
5. Students come in front of camera
6. System shows:
   - **Green box** = Student recognized
   - **Red box** = Unknown person
   - **Name displayed** on recognized faces
7. Attendance marked automatically
8. Session ends after 2 minutes
9. Results saved automatically

**Tips for Best Results:**
- Good lighting in room
- Students face camera one by one
- Wait 1-2 seconds per student
- Avoid multiple faces at once
- Keep camera stable

#### Method B: Scheduled (Automatic)

1. Go to "Attendance Control" tab
2. Click "Schedule Attendance"
3. Set time: `15:00` (3:00 PM)
4. Select subject: `CS101`
5. Click "Set Schedule"
6. System runs automatically at that time
7. No manual intervention needed

**Scheduling Tips:**
- Set 5 minutes before class
- One schedule per day
- Change subject daily
- System runs in background

### 3️⃣ VIEWING REPORTS

#### A. View Attendance Records
1. Go to "Reports & Analytics" tab
2. Click "View Attendance"
3. Filter by subject (optional)
4. See all attendance records
5. Expand details to see:
   - Present students list
   - Absent students list
   - Date and subject

#### B. Today's Absentees
1. Click "Today's Absentees"
2. See list of absent students
3. Shows name, roll number
4. Empty if all present

#### C. Shortage Report
1. Click "Shortage Report"
2. See students below 75%
3. Shows:
   - Name
   - Roll number
   - Present days
   - Total days
   - Percentage
4. Color coded:
   - **Red**: Below 60%
   - **Yellow**: 60-75%

### 4️⃣ STUDENT PORTAL

#### A. Student Login
1. Go to `http://localhost:5000`
2. Select "Student" tab
3. Enter username (set during registration)
4. Enter password
5. Click "Login"

#### B. View Dashboard
- See profile photo
- Check attendance percentage
- View present/absent days
- See shortage alert (if below 75%)

#### C. View Attendance History
1. Click "View Attendance"
2. See complete history
3. Filter by subject
4. Check date-wise status
5. Green = Present, Red = Absent

---

## 🎯 Common Scenarios

### Scenario 1: First Day Setup
```
1. Login as admin
2. Add 3-4 subjects
3. Add 5-10 students with photos
4. Test attendance manually
5. Check reports
6. Give students their login credentials
```

### Scenario 2: Daily Attendance
```
Morning:
1. Login as admin
2. Go to Attendance Control
3. Click "Start Attendance Now"
4. Students come to camera
5. Wait 2 minutes
6. Check "Today's Absentees"
7. Done!
```

### Scenario 3: Subject-wise Tracking
```
1. Schedule attendance for each subject
2. Set different times:
   - CS101: 09:00 AM
   - CS102: 11:00 AM
   - CS103: 02:00 PM
3. System runs automatically
4. View subject-wise reports
```

### Scenario 4: End of Month Report
```
1. Go to "View Attendance"
2. Filter by subject
3. Check shortage report
4. Export Excel file
5. Share with management
```

---

## 🔧 Troubleshooting

### Problem: Camera Not Opening
**Solutions:**
- Check camera permissions in browser
- Close other apps using camera
- Try different browser
- Restart computer
- Check camera is connected

### Problem: Face Not Detected
**Solutions:**
- Improve lighting
- Face camera directly
- Remove glasses/mask
- Move closer to camera
- Ensure face is centered
- Try different angle

### Problem: Wrong Person Recognized
**Solutions:**
- Retake student photo
- Ensure unique faces
- Better lighting during registration
- Adjust recognition threshold
- Remove duplicate photos

### Problem: Student Can't Login
**Solutions:**
- Check username spelling
- Verify password
- Ensure student was added
- Check students_data.json file
- Re-add student if needed

### Problem: Attendance Not Saving
**Solutions:**
- Check attendance_logs folder exists
- Verify write permissions
- Check disk space
- Look for error messages
- Restart application

---

## 📊 Data Management

### Where Data is Stored

**Local Files:**
```
students_data.json       → Student information
subjects.json           → Subject list
attendance_time.json    → Schedule settings
attendance_logs/        → Daily attendance
  ├── 2024-01-15.json
  ├── 2024-01-16.json
  └── ...
student_photos/         → Student photos
data/                   → Face recognition data
attendance_backup.xlsx  → Excel backup
```

### Backup Your Data
```bash
# Create backup folder
mkdir backup

# Copy important files
cp students_data.json backup/
cp subjects.json backup/
cp -r attendance_logs backup/
cp -r student_photos backup/
cp attendance_backup.xlsx backup/
```

### Restore Data
```bash
# Copy from backup
cp backup/students_data.json .
cp backup/subjects.json .
cp -r backup/attendance_logs .
cp -r backup/student_photos .
```

---

## 🎓 Best Practices

### For Administrators

1. **Regular Backups**
   - Backup data weekly
   - Keep multiple copies
   - Test restore process

2. **Student Photos**
   - Good lighting
   - Clear face
   - No accessories
   - Update if needed

3. **Attendance Timing**
   - Start of class
   - 2-minute window
   - One subject at a time
   - Consistent schedule

4. **Report Checking**
   - Daily absentee check
   - Weekly shortage review
   - Monthly reports
   - Share with management

### For Students

1. **Login Credentials**
   - Remember username
   - Keep password safe
   - Don't share account
   - Report issues immediately

2. **During Attendance**
   - Be on time
   - Face camera clearly
   - Wait for green box
   - Don't rush

3. **Check Regularly**
   - Login weekly
   - Verify attendance
   - Report discrepancies
   - Track percentage

---

## 🔐 Security Tips

### For Production Use

1. **Change Default Password**
```python
# In .env file
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=strong_password_here
```

2. **Enable HTTPS**
- Use SSL certificate
- Force HTTPS redirect
- Secure cookies

3. **Password Hashing**
- Implement bcrypt
- Hash student passwords
- Never store plain text

4. **Access Control**
- Limit admin access
- Use strong passwords
- Enable 2FA if possible
- Log all actions

---

## 📱 Mobile Access

Students can access from mobile:
1. Open mobile browser
2. Go to server IP: `http://192.168.1.100:5000`
3. Login as student
4. View attendance
5. Check percentage

---

## 🆘 Getting Help

### Check Logs
```bash
# Run with debug mode
python app_enhanced.py

# Check console output
# Look for error messages
```

### Common Error Messages

**"No face detected"**
- Improve lighting
- Face camera directly
- Retake photo

**"Camera failed to open"**
- Check permissions
- Close other apps
- Restart browser

**"Invalid credentials"**
- Check username/password
- Verify user exists
- Try password reset

---

## 🎉 Success Checklist

- [ ] Application installed
- [ ] Admin login working
- [ ] Subjects added
- [ ] Students added with photos
- [ ] Manual attendance tested
- [ ] Reports accessible
- [ ] Student login working
- [ ] Student can view attendance
- [ ] Scheduled attendance set
- [ ] Data backed up

---

## 📞 Support

For issues:
1. Check this guide
2. Review troubleshooting section
3. Check error messages
4. Verify all dependencies installed
5. Test with single student first

---

**Remember:** This system uses face recognition, so good lighting and clear photos are essential for accurate attendance!

Happy Attendance Tracking! 🎓✨

# 🚀 Smart Attendance System - Quick Reference Card

## ⚡ Quick Start
```bash
pip install -r requirements.txt
python start.py
```
**Access:** http://localhost:5000  
**Admin Login:** bcca / bcca

---

## 🎯 Common Tasks

### Add Student
1. Admin Dashboard → Student Management → Add Student
2. Fill: Username, Name, Roll No, Class, Semester, Password
3. Open Camera → Capture Photo → Submit

### Take Attendance
1. Admin Dashboard → Attendance Control → Start Attendance Now
2. Camera opens (2 min session)
3. Students face camera → Auto-marked
4. Green box = Recognized, Red = Unknown

### Schedule Attendance
1. Attendance Control → Schedule Attendance
2. Set time (e.g., 15:00)
3. Select subject → Set Schedule

### View Reports
1. Reports & Analytics → View Attendance
2. Filter by subject (optional)
3. See present/absent lists

### Student Login
1. Login page → Select "Student"
2. Enter username/password
3. View dashboard and attendance

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `app_enhanced.py` | Main application |
| `students_data.json` | Student database |
| `subjects.json` | Subjects list |
| `attendance_logs/` | Daily attendance |
| `attendance_backup.xlsx` | Excel backup |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera not opening | Check permissions, close other apps |
| Face not detected | Better lighting, face camera directly |
| Wrong recognition | Retake photo, better lighting |
| Can't login | Check username/password spelling |
| Data not saving | Check folder permissions |

---

## 📊 Default Settings

- **Attendance Duration:** 2 minutes
- **Recognition Threshold:** 0.6
- **Minimum Attendance:** 75%
- **Admin Username:** bcca
- **Admin Password:** bcca

---

## 🎨 Color Codes

- 🟢 **Green Box** = Student recognized
- 🔴 **Red Box** = Unknown person
- 🟢 **Present Badge** = Student attended
- 🔴 **Absent Badge** = Student missed
- 🟡 **Warning** = Below 75% attendance

---

## 📱 URLs

| Page | URL |
|------|-----|
| Login | http://localhost:5000 |
| Admin Dashboard | http://localhost:5000/admin/dashboard |
| Student Dashboard | http://localhost:5000/student/dashboard |
| Add Student | http://localhost:5000/admin/add_student |
| Take Attendance | http://localhost:5000/admin/start_attendance |
| View Reports | http://localhost:5000/admin/view_attendance |

---

## 🔑 Keyboard Shortcuts

- **Q** - Quit attendance session early
- **Ctrl+C** - Stop application

---

## 💾 Backup Commands

```bash
# Backup data
cp students_data.json backup/
cp subjects.json backup/
cp -r attendance_logs backup/
cp -r student_photos backup/

# Restore data
cp backup/students_data.json .
cp backup/subjects.json .
```

---

## 📞 Quick Help

**Camera Issues?**
- Check browser permissions
- Try different browser
- Restart computer

**Recognition Issues?**
- Improve lighting
- Retake student photo
- Face camera directly

**Login Issues?**
- Verify credentials
- Check students_data.json
- Re-add student if needed

---

## ✅ Daily Checklist

- [ ] Login as admin
- [ ] Start attendance
- [ ] Check absentees
- [ ] Review shortage report
- [ ] Backup data (weekly)

---

## 🎓 Best Practices

1. **Good Lighting** - Essential for accuracy
2. **Clear Photos** - Face camera directly
3. **Regular Backups** - Weekly recommended
4. **Check Reports** - Daily absentee review
5. **Update Photos** - If recognition fails

---

## 📈 Statistics

- **Setup Time:** 5 minutes
- **Add Student:** 1 minute
- **Attendance Session:** 2 minutes
- **Recognition Speed:** 1-2 seconds/face
- **Accuracy:** >90% (good lighting)

---

## 🔗 Quick Links

- **Full Documentation:** README_ENHANCED.md
- **Usage Guide:** USAGE_GUIDE.md
- **Implementation:** IMPLEMENTATION_SUMMARY.md

---

**Need more help?** Check USAGE_GUIDE.md for detailed instructions!

"""
Smart Attendance System - Initialization Script
Run this once to set up everything
"""
import os
import json
import sys

def create_directories():
    """Create necessary directories"""
    directories = [
        'attendance_logs',
        'student_photos',
        'data',
        'static/css',
        'static/js',
        'templates'
    ]
    
    print("Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ {directory}")

def create_data_files():
    """Create initial data files"""
    print("\nCreating data files...")
    
    # Students data
    if not os.path.exists('students_data.json'):
        with open('students_data.json', 'w') as f:
            json.dump({}, f, indent=2)
        print("  ✓ students_data.json")
    else:
        print("  ⊙ students_data.json (already exists)")
    
    # Subjects
    if not os.path.exists('subjects.json'):
        with open('subjects.json', 'w') as f:
            json.dump([], f, indent=2)
        print("  ✓ subjects.json")
    else:
        print("  ⊙ subjects.json (already exists)")
    
    # Attendance time
    if not os.path.exists('attendance_time.json'):
        with open('attendance_time.json', 'w') as f:
            json.dump({"time": "15:00", "subject": ""}, f, indent=2)
        print("  ✓ attendance_time.json")
    else:
        print("  ⊙ attendance_time.json (already exists)")

def create_env_file():
    """Create .env file if not exists"""
    print("\nChecking environment file...")
    
    if not os.path.exists('.env'):
        env_content = """# Smart Attendance System Configuration

# Admin Credentials (CHANGE THESE IN PRODUCTION!)
ADMIN_USERNAME=bcca
ADMIN_PASSWORD=bcca

# Session Secret (CHANGE THIS IN PRODUCTION!)
SESSION_SECRET=dev-secret-key-change-in-production

# Google Sheets Integration (Optional)
# Leave empty if not using Google Sheets
GOOGLE_CREDS_B64=
GOOGLE_SHEET_ID=
GOOGLE_DRIVE_FOLDER_ID=

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=1
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("  ✓ .env file created")
    else:
        print("  ⊙ .env file (already exists)")

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    
    required_packages = [
        'flask',
        'dotenv',
        'cv2',
        'face-recognition',
        'pandas',
        'openpyxl',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("\nInstall them with:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def create_sample_data():
    """Create sample data for testing"""
    print("\nDo you want to create sample data for testing? (y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        # Sample subjects
        subjects = [
            {"code": "CS101", "name": "Data Structures"},
            {"code": "CS102", "name": "Database Management"},
            {"code": "CS103", "name": "Web Development"}
        ]
        
        with open('subjects.json', 'w') as f:
            json.dump(subjects, f, indent=2)
        
        print("  ✓ Sample subjects created")
        print("    - CS101: Data Structures")
        print("    - CS102: Database Management")
        print("    - CS103: Web Development")

def print_summary():
    """Print setup summary"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 What's Next?")
    print("\n1. Start the application:")
    print("   python app_enhanced.py")
    
    print("\n2. Open your browser:")
    print("   http://localhost:5000")
    
    print("\n3. Login as admin:")
    print("   Username: bcca")
    print("   Password: bcca")
    
    print("\n4. Follow these steps:")
    print("   a. Add subjects (Subject Management)")
    print("   b. Add students with photos (Student Management)")
    print("   c. Take attendance (Attendance Control)")
    print("   d. View reports (Reports & Analytics)")
    
    print("\n📚 Documentation:")
    print("   - Quick Start: QUICK_REFERENCE.md")
    print("   - Full Guide: USAGE_GUIDE.md")
    print("   - Details: README_ENHANCED.md")
    
    print("\n⚠️  Important:")
    print("   - Ensure good lighting for face recognition")
    print("   - Camera permissions required")
    print("   - Change default admin password in production")
    
    print("\n" + "="*60)
    print("Happy Attendance Tracking! 🎓")
    print("="*60 + "\n")

def main():
    """Main initialization function"""
    print("="*60)
    print("🎓 Smart Attendance System - Initialization")
    print("="*60 + "\n")
    
    # Create directories
    create_directories()
    
    # Create data files
    create_data_files()
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Please install missing dependencies first!")
        sys.exit(1)
    
    # Create sample data
    create_sample_data()
    
    # Print summary
    print_summary()
    
    # Ask to start application
    print("Do you want to start the application now? (y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\nStarting application...\n")
        import subprocess
        subprocess.run([sys.executable, "app_enhanced.py"])
    else:
        print("\nYou can start the application later with:")
        print("  python app_enhanced.py\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error during setup: {e}")
        sys.exit(1)

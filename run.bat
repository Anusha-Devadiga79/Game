@echo off
echo ============================================================
echo  Smart Attendance System - Quick Launcher
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from python.org
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Dependencies not found. Installing...
    echo This may take a few minutes...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK!
echo.

REM Check if initialized
if not exist "students_data.json" (
    echo First time setup detected...
    echo Running initialization...
    echo.
    python initialize.py
) else (
    echo System already initialized.
    echo.
)

REM Start the application
echo Starting Smart Attendance System...
echo.
echo Access the application at: http://localhost:5000
echo Default login: bcca / bcca
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python app_enhanced.py

pause

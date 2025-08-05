@echo off
echo Setting up JobGenie ML Engine...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete!
echo.
echo To run the ML engine:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run the ML engine: python match_jobs.py
echo.
echo The ML engine will be available at http://localhost:5000
pause

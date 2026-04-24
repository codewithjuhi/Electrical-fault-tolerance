@echo off
REM Windows Batch Script to run FastAPI and Streamlit

echo.
echo ========================================
echo Electrical Fault Detection ^& Classification
echo FastAPI + Streamlit Deployment
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
python -m pip install --user -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting FastAPI Backend...
echo ========================================
echo FastAPI will run on: http://localhost:8000
echo Swagger Docs: http://localhost:8000/docs
echo.

REM Start FastAPI in background
start cmd /k python main.py

REM Wait for FastAPI to start
timeout /t 3 /nobreak

echo.
echo ========================================
echo Starting Streamlit Frontend...
echo ========================================
echo Streamlit will run on: http://localhost:8501
echo.

REM Start Streamlit
python -m streamlit run app.py

pause

@echo off
setlocal

cd /d %~dp0

echo [1/5] Checking Python virtual environment...
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please install Python and enable "Add python.exe to PATH".
        pause
        exit /b 1
    )
)

echo [2/5] Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [3/5] Pulling latest code...
git pull
if errorlevel 1 (
    echo Git pull failed. Continuing with local code...
)

echo [4/5] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo [5/5] Starting Meta Ads dashboard...
streamlit run app.py

pause

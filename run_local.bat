@echo off
setlocal

cd /d "%~dp0"

echo Starting Shift Management local app...

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Installing requirements...
"venv\Scripts\python.exe" -m pip install --upgrade pip

if exist "requirements.txt" (
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
) else (
    "venv\Scripts\python.exe" -m pip install Flask
)

if errorlevel 1 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b 1
)

echo Opening local app...
"venv\Scripts\python.exe" run_local.py

pause
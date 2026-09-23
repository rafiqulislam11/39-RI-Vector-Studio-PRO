@echo off
title RI Vector Studio PRO v3.2 FIXED
cd /d "%~dp0"
echo ==========================================
echo RI Vector Studio PRO v3.2 FIXED
echo ==========================================
python --version
if errorlevel 1 (
  echo.
  echo Python পাওয়া যায়নি. Python 3.10/3.11 x64 install করুন এবং PATH-এ add করুন.
  pause
  exit /b 1
)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Dependency install failed.
  pause
  exit /b 1
)
echo.
echo Starting RI Vector Studio...
start "" http://127.0.0.1:8000
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pause

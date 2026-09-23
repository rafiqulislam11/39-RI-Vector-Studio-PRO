@echo off
title RI Vector Studio PRO v3.2 DEBUG
cd /d "%~dp0"
echo Starting debug server...
python -m uvicorn main:app --host 127.0.0.1 --port 8000
pause

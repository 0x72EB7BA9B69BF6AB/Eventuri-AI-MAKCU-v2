@echo off
cd /d "%~dp0"
echo [*] Activating venv...
call venv\Scripts\activate
echo [*] Starting Eventuri-AI...
python main.py
pause

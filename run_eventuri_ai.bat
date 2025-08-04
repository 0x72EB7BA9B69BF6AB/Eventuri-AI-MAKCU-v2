@echo off
cd /d "%~dp0src"
echo [*] Activating venv...
call venv\Scripts\activate
echo [*] Starting Eventuri-AI...
python Eventuri-AI.py
pause

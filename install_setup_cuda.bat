@echo off
cd /d "%~dp0"
echo [*] Creating venv and installing dependencies...
python utils/setup/setup_cuda.py
pause

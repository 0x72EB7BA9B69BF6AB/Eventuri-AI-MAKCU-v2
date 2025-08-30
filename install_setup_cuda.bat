@echo off
cd /d "%~dp0"
echo [*] Creating venv and installing dependencies...
python setup_cuda.py
pause

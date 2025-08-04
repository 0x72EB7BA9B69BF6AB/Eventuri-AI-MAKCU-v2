@echo off
cd /d "%~dp0src"
echo [*] Creating venv and installing dependencies...
python setup_directml.py
pause

@echo off
REM ===============================================
REM ArduCheck — Launcher GUI
REM ===============================================
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH.
    pause
    exit /b 1
)

echo Iniciando GUI...
python main.py gui
pause

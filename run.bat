@echo off
REM ===============================================
REM ArduCheck — Launcher consola
REM ===============================================
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH.
    echo Instala Python 3.10+ desde https://python.org
    pause
    exit /b 1
)

echo.
echo ====================================================
echo  ArduCheck  -  Modo consola
echo ====================================================
echo.
echo Comandos disponibles:
echo   1) Escanear puertos
echo   2) Diagnosticar primera placa detectada
echo   3) Diagnosticar un puerto especifico
echo   4) Ver instrucciones de instalacion
echo   5) Salir
echo.

set /p opc=Elige una opcion: 

if "%opc%"=="1" python main.py scan
if "%opc%"=="2" python main.py diagnose
if "%opc%"=="3" (
    set /p port=Puerto (ej. COM3): 
    python main.py diagnose --port %port%
)
if "%opc%"=="4" python main.py install
if "%opc%"=="5" exit

pause

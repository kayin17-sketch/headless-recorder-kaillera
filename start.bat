@echo off
REM Kaillera Headless Recorder - Script de inicio para Windows
echo ================================
echo Kaillera Headless Recorder
echo ================================
echo.

cd /d "%~dp0backend"

if not exist "..\recordings" (
    echo Creando directorio de grabaciones...
    mkdir "..\recordings"
)

echo Iniciando servidor en http://localhost:8000
echo Presiona Ctrl+C para detener
echo.

python main.py

pause

@echo off
REM Kaillera Connection Test - Windows
echo ================================
echo Kaillera Connection Test
echo ================================
echo.

cd /d "%~dp0backend"

if not "%~1"=="" (
    python test_connection.py %~1 %~2
) else (
    python test_connection.py
)

pause

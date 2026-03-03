@echo off
REM Test Kaillera Server Port
echo ================================
echo Kaillera Port Test Tool
echo ================================
echo.

cd /d "%~dp0backend"

python test_port.py kayinremix.duckdns.org 27888

pause

@echo off
REM Simple Kaillera Connection Test
echo ================================
echo Simple Kaillera Connection Test
echo ================================
echo.

cd /d "%~dp0backend"

python simple_test.py kayinremix.duckdns.org 27888

pause

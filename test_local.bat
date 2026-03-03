@echo off
REM Test Local Network Kaillera Server
echo =====================================
echo Local Network Server Test
echo =====================================
echo.

cd /d "%~dp0backend"

python test_local.py

pause

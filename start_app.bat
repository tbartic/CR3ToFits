@echo off
setlocal
cd /d "%~dp0"

py -3 app.py
if errorlevel 1 (
    echo.
    echo Python 3 was not found or the app failed to start.
    echo Please install Python 3 and ensure it is available on PATH.
    pause
)

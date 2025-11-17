@echo off
title X8 AutoEngine Runner
color 0A

echo =============================================
echo        Starting X8 AutoEngine Runner
echo =============================================

REM Navigate to project root
cd /d "%~dp0"

REM Run engine using Python module mode
python -m Engine.Runner.AutoEngine_Runner

echo.
echo =============================================
echo       Engine stopped (CSV finished)
echo  Press any key to close this window...
echo =============================================
pause >nul

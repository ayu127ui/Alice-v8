@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
cls
echo.
echo ========================================
echo   PROJECT-SPECULA: Starting Application
echo ========================================
echo.
python -m app.run
pause

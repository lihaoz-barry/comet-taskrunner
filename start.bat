@echo off
REM Comet Task Runner - Quick Start Script

echo ============================================================
echo Starting Comet Task Runner
echo ============================================================
echo.

REM Start Backend in new window
echo [1/2] Starting Backend...
start "Comet Backend" cmd /k "python src\backend.py"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [2/2] Starting Frontend...
python src\frontend.py

echo.
echo ============================================================
echo Comet Task Runner is running!
echo ============================================================
pause

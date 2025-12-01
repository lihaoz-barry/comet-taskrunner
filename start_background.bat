@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  Comet Task Runner - Background Mode Launcher
REM  Backend: Visible terminal with logs
REM  Frontend: Hidden (pythonw, no console)
REM  Priority: Windows Terminal → PowerShell → CMD
REM ============================================================

echo.
echo ============================================================
echo  Comet Task Runner - Starting (Background Mode)
echo ============================================================
echo.

REM ===== Get script directory and CD to project root =====
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [INFO] Working directory: %CD%
echo [INFO] Mode: Background (Frontend hidden, Backend visible)
echo.

REM ===== Detect Best Terminal =====
set "TERMINAL=cmd"
set "TERMINAL_ARGS=/k"
set "TERMINAL_NAME=CMD"

REM Check for Windows Terminal
where wt.exe >nul 2>&1
if %errorlevel% equ 0 (
    set "TERMINAL=wt.exe"
    set "TERMINAL_NAME=Windows Terminal"
    echo [INFO] Using Windows Terminal ^(best option^)
    goto :terminal_detected
)

REM Check for PowerShell
where powershell.exe >nul 2>&1
if %errorlevel% equ 0 (
    set "TERMINAL=powershell.exe"
    set "TERMINAL_NAME=PowerShell"
    echo [INFO] Using PowerShell
    goto :terminal_detected
)

REM Fallback to CMD
echo [INFO] Using CMD ^(fallback^)

:terminal_detected
echo.

REM ===== Check Dependencies =====
echo [1/3] Checking Python dependencies...
echo.

REM Silent install to avoid clutter (show errors only)
pip install -q -r requirements.txt 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies may need manual installation
    echo [INFO] Run: pip install -r requirements.txt
    echo.
)

echo [OK] Dependencies checked
echo.

REM ===== Detect Backend Version =====
set "BACKEND_CMD=python src\backend.py"
set "BACKEND_VERSION=Python Script"

if exist "dist\backend.exe" (
    set "BACKEND_CMD=dist\backend.exe"
    set "BACKEND_VERSION=Packaged .exe"
    echo [INFO] Found packaged backend.exe - using standalone version
) else (
    echo [INFO] No backend.exe found - using Python script
)
echo.

REM ===== Start Backend =====
echo [2/3] Starting Backend ^(%BACKEND_VERSION%^)...
echo.

if "%TERMINAL%"=="wt.exe" (
    REM Windows Terminal - open in NEW WINDOW (not tab)
    start "" wt.exe -w new --title "Comet Backend" cmd /k "cd /d %CD% && echo Backend starting... && echo. && %BACKEND_CMD%"
) else if "%TERMINAL%"=="powershell.exe" (
    REM PowerShell - open in new window
    start "Comet Backend" powershell.exe -NoExit -Command "cd '%CD%'; Write-Host 'Backend starting...' -ForegroundColor Green; %BACKEND_CMD%"
) else (
    REM CMD - open in new window
    start "Comet Backend" cmd /k "cd /d %CD% && echo Backend starting... && echo. && %BACKEND_CMD%"
)

echo [OK] Backend launched in %TERMINAL_NAME%
echo.

REM ===== Wait for Backend =====
echo [3/3] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul
echo [OK] Backend should be ready
echo.

REM ===== Start Frontend (HIDDEN - No Console) =====
echo Starting Frontend (background mode - no console)...
echo.

REM Use pythonw to launch without console window
start "" pythonw src\frontend.py

echo [OK] Frontend launched in background (no console)
echo.

REM ===== Success =====
echo ============================================================
echo  SUCCESS! Comet Task Runner is now running
echo ============================================================
echo.
echo  - Backend: Running in %TERMINAL_NAME% window (logs visible)
echo  - Frontend: Running in background (no console)
echo.
echo  To see frontend, check your taskbar for the GUI window
echo  To stop: Close backend terminal and frontend GUI
echo.
echo  You can close this window now
echo.
pause

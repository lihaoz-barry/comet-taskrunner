@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  Comet Task Runner - Smart Launcher
REM  Automatically detects and uses the best available terminal
REM  Priority: Windows Terminal → PowerShell → CMD
REM ============================================================

echo.
echo ============================================================
echo  Comet Task Runner - Starting...
echo ============================================================
echo.

REM ===== Get script directory and CD to project root =====
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [INFO] Working directory: %CD%
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
echo [1/4] Checking Python dependencies...
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

REM ===== Check API Key (Security) =====
if not defined COMET_API_KEY (
    if not exist ".env" (
        echo [SECURITY WARNING] COMET_API_KEY not found!
        echo.
        echo The backend now requires an API Key to run securely.
        echo.
        set /p "TEMP_KEY=Please enter a temporary API Key for this session: "
        if defined TEMP_KEY (
            set "COMET_API_KEY=!TEMP_KEY!"
            echo [OK] Temporary key set.
        ) else (
            echo [ERROR] No key provided. Backend will fail to start.
        )
        echo.
    ) else (
        echo [OK] Found .env file (assuming API Key is inside)
    )
) else (
    echo [OK] COMET_API_KEY is set in environment
)
echo.

REM ===== Detect Backend Version =====
set "BACKEND_CMD=python src\backend.py"
set "BACKEND_VERSION=Python Script"

if exist "dist\backend.exe" (
    set "BACKEND_CMD=dist\backend.exe"
    set "BACKEND_VERSION=Packaged .exe"
    echo [INFO] Found packaged backend.exe - using standalone version
) else (
    echo [INFO "No backend.exe found - using Python script
)
echo.

REM ===== Start Backend =====
echo [2/4] Starting Backend ^(%BACKEND_VERSION%^)...
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
echo [3/4] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul
echo [OK] Backend should be ready
echo.

REM ===== Start Frontend =====
echo [4/4] Starting Frontend...
echo.

if "%TERMINAL%"=="wt.exe" (
    REM Windows Terminal - open in NEW WINDOW (not tab)
    start "" wt.exe -w new --title "Comet Frontend" cmd /k "cd /d %CD% && echo Frontend starting... && echo. && python src\frontend.py"
) else if "%TERMINAL%"=="powershell.exe" (
    REM PowerShell - open in new window
    start "Comet Frontend" powershell.exe -NoExit -Command "cd '%CD%'; Write-Host 'Frontend starting...' -ForegroundColor Cyan; python src\frontend.py"
) else (
    REM CMD - open in new window
    start "Comet Frontend" cmd /k "cd /d %CD% && echo Frontend starting... && echo. && python src\frontend.py"
)

echo [OK] Frontend launched in %TERMINAL_NAME%
echo.

REM ===== Success =====
echo ============================================================
echo  SUCCESS! Comet Task Runner is now running
echo ============================================================
echo.
echo  - Backend: Running in separate %TERMINAL_NAME% window
echo  - Frontend: Running in separate %TERMINAL_NAME% window
echo  - You can close this window now
echo.
echo  Press any key to exit...
pause >nul

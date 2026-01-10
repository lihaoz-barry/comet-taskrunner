@echo off
setlocal enabledelayedexpansion
REM ============================================================
REM Build CometTaskRunnerTray.exe using PyInstaller
REM Creates a standalone tray application (no console window)
REM ============================================================

echo.
echo ============================================================
echo  Building CometTaskRunnerTray.exe with PyInstaller
echo ============================================================
echo.

if exist "dist\CometTaskRunnerTray.exe" (
    echo [INFO] Stopping any running instance...
    taskkill /F /IM CometTaskRunnerTray.exe 2>nul
    if %errorlevel% == 0 (
        echo [SUCCESS] Stopped running instance
        timeout /t 2 /nobreak >nul
    )
    
    echo [INFO] Removing old CometTaskRunnerTray.exe...
    del /q dist\CometTaskRunnerTray.exe
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to delete old exe. Please close it manually.
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Starting PyInstaller build...
echo.

REM Run PyInstaller with tray spec file
pyinstaller CometTaskRunnerTray.spec --noconfirm

REM Check PyInstaller exit code
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo  BUILD FAILED - PyInstaller Error
    echo ============================================================
    echo.
    echo  PyInstaller encountered an error (exit code: %errorlevel%).
    echo  Please check the error messages above.
    echo.
    pause
    exit /b 1
)

REM Wait a moment for file system to flush writes
timeout /t 1 /nobreak >nul 2>&1

echo.
echo [INFO] Verifying build output...
echo.

REM Check if build output exists (more reliable than errorlevel)
if exist "dist\CometTaskRunnerTray.exe" (
    echo ============================================================
    echo  BUILD SUCCESSFUL
    echo ============================================================
    echo.
    echo  Output: dist\CometTaskRunnerTray.exe
    
    REM Show file size
    for %%A in (dist\CometTaskRunnerTray.exe) do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
        echo  Size: !sizeMB! MB
    )
    
    echo.
    echo  Features:
    echo  - System tray icon ^(no console window^)
    echo  - Background Flask server
    echo  - Real-time log streaming ^(Show Logs^)
    echo.
    echo  To run: dist\CometTaskRunnerTray.exe
    echo.
) else (
    echo ============================================================
    echo  BUILD FAILED
    echo ============================================================
    echo.
    echo  Error: dist\CometTaskRunnerTray.exe not found
    echo  Check the PyInstaller output above for errors
    echo.
)

pause

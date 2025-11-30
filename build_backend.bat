@echo off
REM ============================================================
REM Build backend.exe using PyInstaller
REM This creates a standalone executable with all dependencies
REM ============================================================

echo.
echo ============================================================
echo  Building backend.exe with PyInstaller
echo ============================================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] PyInstaller not found, installing...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Clean previous builds
if exist "build" (
    echo [INFO] Cleaning previous build directory...
    rmdir /s /q build
)

if exist "dist\backend.exe" (
    echo [INFO] Removing old backend.exe...
    del /q dist\backend.exe
)

echo.
echo [INFO] Starting PyInstaller build...
echo.

REM Run PyInstaller with spec file
pyinstaller backend.spec

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo  BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo  Output: dist\backend.exe
    
    REM Show file size
    for %%A in (dist\backend.exe) do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
        echo  Size: !sizeMB! MB
    )
    
    echo.
    echo  Next steps:
    echo  1. Test: dist\backend.exe
    echo  2. Check terminal output for errors
    echo  3. Verify Flask starts on port 5000
    echo.
) else (
    echo.
    echo [ERROR] Build failed! Check the output above for errors
    echo.
)

pause

@echo off
REM ------------------------------------------------------------
REM Build script for the tray‑icon executable (CometTaskRunner)
REM Extends the existing build_backend.bat and adds tray‑specific steps.
REM ------------------------------------------------------------

REM 1. Run the existing backend build (may be a no‑op if already up‑to‑date)
rem call build_backend.bat

REM 2. Ensure a virtual environment is active (reuse same as backend)
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

REM 3. Install core and tray dependencies
pip install --quiet -r requirements.txt
pip install --quiet pyinstaller pystray Pillow pywin32

REM 4. Ensure the resources folder exists
if not exist resources (
    mkdir resources
)

REM 5. Convert the generated PNG icon to ICO if not already present
if not exist resources\comet.ico (
    if exist resources\tray_icon.png (
        echo Converting tray_icon.png to ICO using Python...
        python resources\convert_icon.py
    ) else (
        echo [WARNING] tray_icon.png not found – please ensure the icon PNG is placed in the resources folder.
    )
)

REM 6. Build the tray executable
set PYTHONPATH=%PYTHONPATH%;%CD%\src
pyinstaller --onefile --noconsole ^
    --add-data "resources;resources" ^
    --add-data "workflows;workflows" ^
    --paths "src" ^
    --collect-submodules tasks ^
    --collect-submodules workflow ^
    --collect-submodules utils ^
    --collect-submodules overlay ^
    --icon "resources\comet.ico" ^
    --name CometTaskRunnerTray ^
    src\tray\icon_tray.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Tray build failed!
    exit /b %ERRORLEVEL%
)

echo Tray build complete. Output: dist\CometTaskRunnerTray.exe
pause

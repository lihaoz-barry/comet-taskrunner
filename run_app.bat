@echo off
echo Starting Comet Task Runner...

:: Install dependencies (suppress output if already satisfied to speed up)
echo Checking dependencies...
pip install -r requirements.txt >nul 2>&1

:: Launch the Frontend (which will launch the Backend automatically)
:: usage of pythonw hides the frontend console.
echo Launching Application...
start pythonw src\frontend.py

:: Exit this terminal
exit

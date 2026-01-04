import sys
import os
import threading
import logging
import argparse
import webbrowser
import subprocess
import shutil
import pystray
from PIL import Image

# Add src to path for internal imports
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.append(src_path)

# Import backend startup
try:
    from backend import run_server
except ImportError:
    # If running from bundled EXE, the structure might be different
    import backend
    run_server = backend.run_server

# Set up logging using the unified logger
from utils.logger import setup_logging
logger = setup_logging()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)

import winreg

def toggle_autolaunch(icon, item):
    """Toggle application auto-launch on Windows startup."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "CometTaskRunner"
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        try:
            # Check if it exists
            winreg.QueryValueEx(key, app_name)
            # If successful, it exists, so remove it
            winreg.DeleteValue(key, app_name)
            logger.info("Auto-launch disabled.")
        except FileNotFoundError:
            # Not found, so add it
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            logger.info(f"Auto-launch enabled for {exe_path}")
        winreg.CloseKey(key)
    except Exception as e:
        logger.error(f"Failed to toggle auto-launch: {e}")

def open_monitor(icon, item):
    """Open the local health check."""
    webbrowser.open("http://localhost:5000/health")

def show_logs(icon, item):
    """Open the log file in a real-time streaming terminal."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    log_path = os.path.join(base_dir, "logs", "comet.log")
    
    # Ensure log file exists before trying to tail it
    if not os.path.exists(log_path):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a') as f:
            pass

    ps_wait_command = f"Get-Content -Path '{log_path}' -Wait -Tail 100 -Encoding utf8"
    
    wt_path = shutil.which("wt.exe")
    
    try:
        if wt_path:
            # Option 1: Windows Terminal (Most premium experience)
            cmd = f'wt.exe --title "Comet TaskRunner Logs" powershell.exe -NoExit -Command "{ps_wait_command}"'
            subprocess.Popen(cmd, shell=True)
            logger.info("Launched logs in Windows Terminal.")
        else:
            # Option 2: Basic PowerShell
            cmd = f'powershell.exe -NoExit -Command "$Host.UI.RawUI.WindowTitle = \'Comet TaskRunner Logs\'; {ps_wait_command}"'
            subprocess.Popen(cmd, shell=True)
            logger.info("Launched logs in PowerShell.")
    except Exception as e:
        logger.error(f"Failed to launch terminal: {e}")
        os.startfile(log_path)

def exit_app(icon, item):
    """Gracefully shutdown and exit."""
    icon.stop()
    os._exit(0)

def main():
    # 1. Start Backend in a background thread
    backend_thread = threading.Thread(target=run_server, daemon=True)
    backend_thread.start()
    logger.info("Backend thread started.")

    # 2. Setup Tray Icon
    icon_file = resource_path("resources/comet.ico")
    if not os.path.exists(icon_file):
        logger.error(f"Icon not found at {icon_file}. Falling back to blank image.")
        image = Image.new('RGB', (64, 64), color='blue')
    else:
        image = Image.open(icon_file)

    menu = (
        pystray.MenuItem("Open Monitor", open_monitor),
        pystray.MenuItem("Show Logs", show_logs),
        pystray.MenuItem("Toggle Auto-Launch", toggle_autolaunch),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", exit_app),
    )

    icon = pystray.Icon("CometTaskRunner", image, "Comet Task Runner", menu)
    
    logger.info("Tray icon running.")
    icon.run()

if __name__ == "__main__":
    main()

"""
Comet Task Runner - Tray Application Entry Point

This module provides a system tray icon for the Comet Task Runner backend.
The backend runs in a background thread while the tray icon handles user interaction.

Features:
- System tray icon with menu
- Show Logs: Opens a terminal with real-time log streaming
- Exit: Gracefully shuts down the application

Usage:
    python src/tray/icon_tray.py
    
Or when packaged:
    CometTaskRunnerTray.exe
"""

import sys
import os
import threading
import logging
import subprocess
import shutil

# Add src to path for internal imports
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pystray
from PIL import Image

# Import backend startup function
from backend import run_server

# Set up logging using the unified logger
from utils.logger import setup_logging
logger = setup_logging()


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)


def get_log_path() -> str:
    """Get the path to the log file."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    log_path = os.path.join(base_dir, "logs", "comet.log")
    
    # Ensure log directory and file exist
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, 'a') as f:
            pass
    
    return log_path


def show_logs(icon, item):
    """
    Open the log file in a real-time streaming terminal.
    
    Uses Windows Terminal if available, otherwise falls back to PowerShell.
    The terminal will tail the log file with -Wait for real-time updates.
    """
    log_path = get_log_path()
    
    # PowerShell command to tail the log file
    ps_command = f"Get-Content -Path '{log_path}' -Wait -Tail 100 -Encoding utf8"
    
    # Check if Windows Terminal is available
    wt_path = shutil.which("wt.exe")
    
    try:
        if wt_path:
            # Windows Terminal (premium experience)
            cmd = f'wt.exe --title "Comet TaskRunner Logs" powershell.exe -NoExit -Command "{ps_command}"'
            subprocess.Popen(cmd, shell=True)
            logger.info("Launched logs in Windows Terminal")
        else:
            # Fallback to PowerShell
            cmd = f'powershell.exe -NoExit -Command "$Host.UI.RawUI.WindowTitle = \'Comet TaskRunner Logs\'; {ps_command}"'
            subprocess.Popen(cmd, shell=True)
            logger.info("Launched logs in PowerShell")
    except Exception as e:
        logger.error(f"Failed to launch terminal: {e}")
        # Last resort: open log file directly
        try:
            os.startfile(log_path)
        except:
            pass


def open_health_check(icon, item):
    """Open the health check endpoint in browser."""
    import webbrowser
    webbrowser.open("http://localhost:5000/health")


def exit_app(icon, item):
    """Gracefully shutdown and exit."""
    logger.info("Exit requested from tray menu")
    icon.stop()
    os._exit(0)


def load_icon_image() -> Image.Image:
    """Load the tray icon image."""
    # Try to load custom icon
    icon_paths = [
        resource_path("Resources/comet_icon.png"),
        resource_path("resources/comet.ico"),
        resource_path("Resources/comet_icon.ico"),
    ]
    
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                logger.info(f"Loaded icon from: {icon_path}")
                return img
            except Exception as e:
                logger.warning(f"Failed to load icon {icon_path}: {e}")
    
    # Fallback: generate simple icon
    logger.warning("Using generated fallback icon")
    from PIL import ImageDraw
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle([12, 12, 52, 52], fill='#00CCCC', outline='#008888', width=2)
    draw.rectangle([20, 24, 28, 32], fill='#1a1a1a')  # Left eye
    draw.rectangle([36, 24, 44, 32], fill='#1a1a1a')  # Right eye
    draw.rectangle([24, 40, 40, 44], fill='#1a1a1a')  # Mouth
    return image


def main():
    """Main entry point for tray application."""
    logger.info("=" * 60)
    logger.info("Starting Comet Task Runner (Tray Mode)")
    logger.info("=" * 60)
    
    # 1. Start Backend in a background thread
    backend_thread = threading.Thread(target=run_server, args=(True,), daemon=True)
    backend_thread.start()
    logger.info("Backend thread started")
    
    # 2. Setup Tray Icon
    image = load_icon_image()
    
    menu = pystray.Menu(
        pystray.MenuItem("Open Health Check", open_health_check),
        pystray.MenuItem("Show Logs", show_logs),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", exit_app),
    )
    
    icon = pystray.Icon("CometTaskRunner", image, "Comet Task Runner", menu)
    
    logger.info("Tray icon running")
    logger.info("Right-click tray icon for options")
    logger.info("=" * 60)
    
    # This blocks until exit_app is called
    icon.run()


if __name__ == "__main__":
    main()

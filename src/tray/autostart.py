"""
Windows Autostart Utility Module

This module provides functionality to enable/disable Windows autostart for
the Comet Task Runner application using the Registry Run Key method.

Registry Path: HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
Key Name: CometTaskRunner
"""

import winreg
import sys
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Registry configuration
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "CometTaskRunner"


def get_exe_path() -> str:
    """
    Get the path to the executable that should be auto-started.
    
    Returns:
        str: Full path to the executable (with quotes for safety)
    
    Note:
        - In packaged mode (PyInstaller): Returns path to .exe
        - In development mode: Returns path to Python script
          (but autostart is not recommended in dev mode)
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return f'"{sys.executable}"'
    else:
        # Running in development mode
        # Get path to icon_tray.py
        script_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'icon_tray.py'
        ))
        return f'"{sys.executable}" "{script_path}"'


def is_autostart_enabled() -> bool:
    """
    Check if autostart is currently enabled.
    
    Returns:
        bool: True if autostart registry key exists, False otherwise
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_PATH,
            0,
            winreg.KEY_READ
        )
        try:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            logger.debug(f"Autostart is enabled: {value}")
            return True
        except FileNotFoundError:
            # Key exists but our value doesn't
            winreg.CloseKey(key)
            return False
    except OSError as e:
        logger.error(f"Failed to check autostart status: {e}")
        return False


def enable_autostart() -> bool:
    """
    Enable Windows autostart by adding registry key.
    
    Returns:
        bool: True if successful, False on error
    """
    try:
        exe_path = get_exe_path()
        
        # Only allow in frozen (packaged) mode by default
        if not getattr(sys, 'frozen', False):
            logger.warning(
                "Autostart in development mode is not recommended. "
                "Package the application first using build_tray.bat"
            )
            # Uncomment the following line to block dev mode autostart:
            # return False
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_PATH,
            0,
            winreg.KEY_WRITE
        )
        
        winreg.SetValueEx(
            key,
            APP_NAME,
            0,
            winreg.REG_SZ,
            exe_path
        )
        
        winreg.CloseKey(key)
        logger.info(f"Autostart enabled: {exe_path}")
        return True
        
    except PermissionError:
        logger.error("Permission denied: Cannot modify registry. Contact your administrator.")
        return False
    except OSError as e:
        logger.error(f"Failed to enable autostart: {e}")
        return False


def disable_autostart() -> bool:
    """
    Disable Windows autostart by removing registry key.
    
    Returns:
        bool: True if successful, False on error
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_PATH,
            0,
            winreg.KEY_WRITE
        )
        
        try:
            winreg.DeleteValue(key, APP_NAME)
            winreg.CloseKey(key)
            logger.info("Autostart disabled")
            return True
        except FileNotFoundError:
            # Value doesn't exist, that's fine
            winreg.CloseKey(key)
            logger.debug("Autostart was already disabled")
            return True
            
    except PermissionError:
        logger.error("Permission denied: Cannot modify registry. Contact your administrator.")
        return False
    except OSError as e:
        logger.error(f"Failed to disable autostart: {e}")
        return False


def toggle_autostart() -> bool:
    """
    Toggle autostart state (enable if disabled, disable if enabled).
    
    Returns:
        bool: True if operation successful, False on error
    """
    if is_autostart_enabled():
        return disable_autostart()
    else:
        return enable_autostart()


# CLI test interface
if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Manage Windows autostart for Comet Task Runner")
    parser.add_argument(
        'action',
        choices=['status', 'enable', 'disable', 'toggle'],
        help='Action to perform'
    )
    
    args = parser.parse_args()
    
    if args.action == 'status':
        enabled = is_autostart_enabled()
        print(f"Autostart is {'ENABLED' if enabled else 'DISABLED'}")
        if enabled:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
                value, _ = winreg.QueryValueEx(key, APP_NAME)
                print(f"Path: {value}")
                winreg.CloseKey(key)
            except:
                pass
    
    elif args.action == 'enable':
        success = enable_autostart()
        print(f"Enable autostart: {'SUCCESS' if success else 'FAILED'}")
    
    elif args.action == 'disable':
        success = disable_autostart()
        print(f"Disable autostart: {'SUCCESS' if success else 'FAILED'}")
    
    elif args.action == 'toggle':
        success = toggle_autostart()
        enabled = is_autostart_enabled()
        print(f"Toggle autostart: {'SUCCESS' if success else 'FAILED'}")
        print(f"New status: {'ENABLED' if enabled else 'DISABLED'}")

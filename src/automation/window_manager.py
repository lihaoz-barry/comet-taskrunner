"""
Automation Module - Window Management

Handles window detection, activation, and management for Comet browser.
Extracted from OpenCV-sample demo_image_ui.py
"""

import time
import ctypes
import logging
import winreg
from pathlib import Path
from typing import Optional, Tuple
import win32gui
import win32process
import win32con
import win32api

logger = logging.getLogger(__name__)


class WindowManager:
    """
    Window detection and activation for Comet browser.
    
    Features:
    - Find windows by title keywords
    - Force window activation (ALT key method)
    - Multi-monitor support
    - Registry-based application path lookup
    """
    
    @staticmethod
    def find_comet_window(keywords: list = None, exclude_title: str = None, require_process: str = None) -> Optional[Tuple[int, Tuple[int, int, int, int]]]:
        """
        Find Comet browser window by title and optionally process name.
        
        Args:
            keywords: List of keywords to search
            exclude_title: Optional string, skip window if title contains this
            require_process: Optional string, exact process name (e.g. "comet.exe")
            
        Returns:
            Tuple of (hwnd, rect) or None if not found
        """
        if keywords is None:
            keywords = ["Comet", "Perplexity"]
            
        # Keywords to explicitly exclude (to avoid matching the backend console, IDE, or file explorer)
        exclude_keywords = ["backend.exe", "python.exe", "cmd.exe", "powershell.exe", ".py", 
                          "comet-taskrunner", "Antigravity", "Visual Studio Code"]
        # Also exclude based on param
        if exclude_title:
            exclude_keywords.append(exclude_title)
        
        logger.info(f"Searching for window with keywords: {keywords} (excluding: {exclude_keywords}, process: {require_process})")
        
        found_windows = []
        
        def enum_callback(hwnd, _):
            if not WindowManager._is_candidate_window(hwnd):
                return True
            
            try:
                title = win32gui.GetWindowText(hwnd).lower()
                
                # Check exclusion list first
                if any(ex.lower() in title for ex in exclude_keywords):
                    return True
                
                # Check if ANY keyword matches
                if any(keyword.lower() in title for keyword in keywords):
                    # Check Process Name if required
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if require_process:
                        proc_name = WindowManager._get_process_name(pid)
                        if not proc_name or proc_name.lower() != require_process.lower():
                            # mismatch
                            return True

                    rect = win32gui.GetWindowRect(hwnd)
                    found_windows.append({
                        'hwnd': hwnd,
                        'title': win32gui.GetWindowText(hwnd),
                        'rect': rect,
                        'pid': pid
                    })
            except Exception as e:
                # logger.warning(f"Error checking window {hwnd}: {e}")
                pass
            
            return True
        
        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception as e:
            logger.error(f"Window enumeration failed: {e}")
            return None
        
        if not found_windows:
            logger.warning(f"No match found for keywords={keywords}, process={require_process}")
            return None
        
        # Use first window
        window = found_windows[0]
        logger.info(f"Found window: HWND={window['hwnd']}, Title='{window['title']}', PID={window['pid']}")
        
        return (window['hwnd'], window['rect'])

    @staticmethod
    def _get_process_name(pid: int) -> Optional[str]:
        """Get executable name from PID"""
        try:
            # Try psutil first if available (cleaner)
            try:
                import psutil
                return psutil.Process(pid).name()
            except ImportError:
                pass
                
            # Fallback to pywin32
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            try:
                path = win32process.GetModuleFileNameEx(handle, 0)
                return Path(path).name
            finally:
                win32api.CloseHandle(handle)
        except Exception:
            return None
    
    @staticmethod
    def activate_window(hwnd: int) -> bool:
        """
        Forcefully activate a window and bring it to foreground.
        
        Uses multiple techniques to bypass Windows foreground lock:
        1. ALT key simulation
        2. AttachThreadInput  
        3. Combined aggressive approach
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful
        """
        logger.info(f"Forcefully activating window HWND={hwnd}")
        
        try:
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                logger.info("Window is minimized, restoring...")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)
            
            # Method 1: ALT key (most reliable)
            logger.debug("Trying ALT key method...")
            try:
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                time.sleep(0.05)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                time.sleep(0.1)
                if win32gui.GetForegroundWindow() == hwnd:
                    window_title = win32gui.GetWindowText(hwnd)
                    logger.info(f"Window activated (ALT method): '{window_title}'")
                    return True
            except Exception as e:
                logger.warning(f"ALT method failed: {e}")
            
            # Method 2: Thread attachment
            logger.debug("Trying thread attachment method...")
            try:
                foreground_hwnd = win32gui.GetForegroundWindow()
                if foreground_hwnd:
                    foreground_tid = win32process.GetWindowThreadProcessId(foreground_hwnd)[0]
                    target_tid = win32process.GetWindowThreadProcessId(hwnd)[0]
                    
                    ctypes.windll.user32.AttachThreadInput(target_tid, foreground_tid, True)
                    win32gui.BringWindowToTop(hwnd)
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    win32gui.SetForegroundWindow(hwnd)
                    ctypes.windll.user32.AttachThreadInput(target_tid, foreground_tid, False)
                    
                    time.sleep(0.1)
                    if win32gui.GetForegroundWindow() == hwnd:
                        window_title = win32gui.GetWindowText(hwnd)
                        logger.info(f"Window activated (thread method): '{window_title}'")
                        return True
            except Exception as e:
                logger.warning(f"Thread method failed: {e}")
            
            # Method 3: Combined aggressive
            logger.debug("Trying combined method...")
            try:
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetFocus(hwnd)
                win32gui.SetForegroundWindow(hwnd)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                time.sleep(0.15)
                if win32gui.GetForegroundWindow() == hwnd:
                    window_title = win32gui.GetWindowText(hwnd)
                    logger.info(f"Window activated (combined method): '{window_title}'")
                    return True
            except Exception as e:
                logger.warning(f"Combined method failed: {e}")
            
            # All methods failed
            logger.error("All activation methods failed")
            try:
                win32gui.FlashWindow(hwnd, True)
                logger.info("Flashing window to notify user")
            except:
                pass
            
            return False
                
        except Exception as e:
            logger.error(f"Complete failure to activate window: {e}")
            return False
    
    @staticmethod
    def close_window(hwnd: int) -> bool:
        """
        Close a window using WM_CLOSE message.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if message sent successfully
        """
        try:
            logger.info(f"Closing window HWND={hwnd}")
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to close window: {e}")
            return False

    @staticmethod
    def get_application_path(registry_subkey: str, fallback_path: str) -> Optional[str]:
        """
        Find application executable path via registry or fallback.
        
        Args:
            registry_subkey: Registry path (e.g., "Software\\...\\comet.exe")
            fallback_path: Fallback file path
            
        Returns:
            Path to executable or None
        """
        logger.info("Searching for application path...")
        
        # Try registry
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, registry_subkey),
            (winreg.HKEY_LOCAL_MACHINE, registry_subkey)
        ]
        
        for hkey, subkey in registry_paths:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    path, _ = winreg.QueryValueEx(key, "")
                    if path and Path(path).exists():
                        logger.info(f"Found in registry: {path}")
                        return path
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.warning(f"Registry error: {e}")
        
        # Try fallback
        if fallback_path and Path(fallback_path).exists():
            logger.info(f"Found at fallback location: {fallback_path}")
            return fallback_path
        
        logger.error("Application not found in registry or fallback location")
        return None
    
    @staticmethod
    def _is_candidate_window(hwnd: int) -> bool:
        """
        Check if a window is a candidate (visible, not minimized, non-zero size).
        
        Allows negative coordinates for multi-monitor setups.
        """
        if not win32gui.IsWindowVisible(hwnd):
            return False
        
        if win32gui.IsIconic(hwnd):
            return False
        
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            if width <= 0 or height <= 0:
                return False
        except Exception:
            return False
        
        return True

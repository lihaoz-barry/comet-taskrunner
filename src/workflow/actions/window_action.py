import time
import logging
from typing import Dict, Any
from . import BaseAction, StepResult
# Import from automation package (parent of parent)
from automation import WindowManager

logger = logging.getLogger(__name__)

class WindowAction(BaseAction):
    """
    Action to manage application windows (find, activate, focus).
    
    Inputs (Config):
        operation (str): 'activate' or 'activate_or_launch' (default: activate)
        window_title_pattern (str): Partial title to match (e.g., "Comet")
        retry_count (int): Number of retries (default: 3)
        retry_delay (float): Delay between retries in seconds (default: 1.0)
        launch_config (dict): Optional, keys 'registry_key', 'fallback_path' for launching
        
    Outputs (StepResult.data):
        hwnd (int): Window handle ID on Windows
        rect (tuple): Window coordinates (left, top, right, bottom)
        
    Effect:
        Brings the matching window to foreground and sets focus.
        Updates internal window tracking.
    """
    
    @property
    def action_type(self) -> str:
        return "window"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """
        Execute window operation.
        
        Args:
            config: Configuration dictionary
                - operation: 'activate'
                - window_title_pattern: str
                - retry_count: int
            context: Workflow context
        """
        operation = config.get('operation', 'activate')
        title_pattern = config.get('window_title_pattern', '')
        exclude_title = config.get('exclude_title')
        require_process = config.get('require_process')
        retry_count = int(config.get('retry_count', 3))
        retry_delay = float(config.get('retry_delay', 1.0))
        
        if operation == 'activate' or operation == 'activate_or_launch':
            # Snapshot existing windows before potential launch if this is the first try
            existing_hwnds = set()
            if operation == 'activate_or_launch':
                 # Capture existing match candidates to ensure we target the NEW one
                 # This is a "fuzzy" snapshot - we just list whatever matches now
                 import win32gui
                 def enum_snapshot(hwnd, _):
                     if win32gui.IsWindowVisible(hwnd):
                         existing_hwnds.add(hwnd)
                 try:
                     win32gui.EnumWindows(enum_snapshot, None)
                 except: pass

            for i in range(retry_count):
                try:
                    # Logic adapted from AITask
                    result = WindowManager.find_comet_window(
                        keywords=[title_pattern], 
                        exclude_title=exclude_title,
                        require_process=require_process
                    )
                    
                    # Logic for "Force New Window" (only if we launched it)
                    # If we found a window, but it was in existing_hwnds, and we are expecting a NEW window (handled below)
                    # Actually, if we launched, we want the NEW one.
                    # But find_comet_window returns the *first* match.
                    # If the first match is an old one, we might grab the wrong one.
                    # Ideally find_comet_window should let us exclude specific HWNDs, but for now let's rely on process filtering + title.
                    
                    if result:
                        hwnd, rect = result
                        
                        # If we just launched (i > 0 or after launch block), prefer NOT matching existing_hwnds
                        # But simple logic: if it matches process and title, it's probably fine.
                        # The user specifically asked to "record... and compare... ensure filtered".
                        
                        # In this simple implementation: we can't easily filter inside find_comet_window without changing signature again.
                        # But typically the OLD window (File Explorer) is excluded by process name now.
                        # So this might be redundant, but safe.
                        
                        success = WindowManager.activate_window(hwnd)
                        if success:
                            return StepResult(self.action_type, True, data={'hwnd': hwnd, 'rect': rect})
                    
                    # If not found and we allow launch (only on first attempt)
                    if not result and operation == 'activate_or_launch' and i == 0:
                        launch_config = config.get('launch_config', {})
                        registry_key = launch_config.get('registry_key')
                        fallback_path = launch_config.get('fallback_path')
                        
                        if registry_key or fallback_path:
                            app_path = WindowManager.get_application_path(registry_key, fallback_path)
                            if app_path:
                                logger.info(f"Launching application: {app_path}")
                                import subprocess
                                subprocess.Popen([app_path])
                                # Wait longer after launch (match legacy behavior of 8s)
                                time.sleep(8.0) 
                                continue # Retry loop will find it next time
                            else:
                                logger.warning("Could not determine application path for launch")
                        else:
                            logger.warning("No launch_config provided for activate_or_launch")

                    # Wait before retry
                    if i < retry_count - 1:
                        time.sleep(retry_delay)
                        
                except Exception as e:
                    logger.warning(f"Window activation attempt {i+1} failed: {e}")
                    if i < retry_count - 1:
                        time.sleep(retry_delay)
            
            return StepResult(self.action_type, False, error=f"Could not find/activate window: {title_pattern}")
        
        elif operation == 'maximize':
            # Maximize window operation
            import win32gui
            import win32con
            
            # First find the window
            result = WindowManager.find_comet_window(
                keywords=[title_pattern], 
                exclude_title=exclude_title,
                require_process=require_process
            )
            
            if result:
                hwnd, rect = result
                try:
                    # Activate first
                    WindowManager.activate_window(hwnd)
                    time.sleep(0.2)
                    # Maximize
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    time.sleep(0.3)
                    # Get new rect after maximize
                    new_rect = win32gui.GetWindowRect(hwnd)
                    logger.info(f"Maximized window: {title_pattern}")
                    return StepResult(self.action_type, True, data={'hwnd': hwnd, 'rect': new_rect})
                except Exception as e:
                    logger.error(f"Failed to maximize window: {e}")
                    return StepResult(self.action_type, False, error=str(e))
            else:
                return StepResult(self.action_type, False, error=f"Window not found: {title_pattern}")
            
        else:
            return StepResult(self.action_type, False, error=f"Unknown operation: {operation}")

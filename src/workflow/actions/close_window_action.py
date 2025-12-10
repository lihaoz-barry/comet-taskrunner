import time
from typing import Dict, Any
from . import BaseAction, StepResult
from automation import WindowManager

class CloseWindowAction(BaseAction):
    """
    Action to close an application window.
    
    Inputs (Config):
        window_title_pattern (str): Partial title to find window (optional)
        operation (str): 'close' (default)
        
    Outputs (StepResult.data):
        hwnd (int): The handle of the closed window
        
    Effect:
        Sends WM_CLOSE message to the window.
    """
    
    @property
    def action_type(self) -> str:
        return "close_window"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute close window action"""
        title_pattern = config.get('window_title_pattern')
        
        # If no title provided, try to use last known HWND from context?
        # For now, let's require finding it or using cached
        hwnd = None
        
        if title_pattern:
            result = WindowManager.find_comet_window(keywords=[title_pattern])
            if result:
                hwnd, _ = result
        
        # Fallback to context if available (and no specific title requested)
        if not hwnd and not title_pattern:
             # This assumes previous window action stored it. 
             # But usually context stores step outputs. We'd need to look up a variable.
             # Let's simple require title pattern for now to be safe, or user passes explicit HWND
             pass

        if not hwnd:
            return StepResult(self.action_type, False, error="No window found to close (provide window_title_pattern)")
            
        success = WindowManager.close_window(hwnd)
        
        if success:
             return StepResult(self.action_type, True, data={'hwnd': hwnd})
        else:
             return StepResult(self.action_type, False, error=f"Failed to close window {hwnd}")

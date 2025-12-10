import time
from typing import Dict, Any
from . import BaseAction, StepResult
from automation import MouseController

class ClickAndTypeAction(BaseAction):
    """
    Action to click a location (e.g., input field) and type text.
    
    Inputs (Config):
        coordinates (list/tuple): [x, y] to click before typing
        text (str): The text content to type
        pre_click_delay (float): Delay before clicking (default: 0.1)
        typing_delay (float): Interval between keystrokes (default: 0.05)
        post_type_delay (float): Delay after typing (default: 0.5)
        
    Outputs (StepResult.data):
        typed_length (int): Length of string typed
        
    Effect:
        Moves mouse, clicks, and simulates keyboard input character by character.
    """
    
    @property
    def action_type(self) -> str:
        return "click_and_type"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute click and type action"""
        coordinates = config.get('coordinates')
        text = config.get('text')
        
        if not coordinates:
            return StepResult(self.action_type, False, error="Missing coordinates")
        if text is None:
            return StepResult(self.action_type, False, error="Missing text")
            
        pre_click_delay = float(config.get('pre_click_delay', 0.1))
        post_type_delay = float(config.get('post_type_delay', 0.5))
        typing_delay = float(config.get('typing_delay', 0.05))
        
        # Click
        time.sleep(pre_click_delay)
        x, y = coordinates
        MouseController.click(x, y)
        time.sleep(0.3)
        
        # Type
        MouseController.type_text(str(text), interval=typing_delay)
        
        time.sleep(post_type_delay)
        
        return StepResult(self.action_type, True, data={'typed_length': len(str(text))})

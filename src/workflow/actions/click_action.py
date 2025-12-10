import time
from typing import Dict, Any
from . import BaseAction, StepResult
from automation import MouseController

class ClickAction(BaseAction):
    """
    Action to click mouse at specific coordinates.
    
    Inputs (Config):
        coordinates (list/tuple): [x, y] coordinates to click
        click_type (str): 'single', 'double', 'right' (default: 'single')
        pre_delay (float): Wait before click (default: 0.1s)
        post_delay (float): Wait after click (default: 0.5s)
        
    Outputs (StepResult.data):
        clicked_at (tuple): The coordinates clicked
        
    Effect:
        Moves mouse cursor to {coordinates}.
        Performs the specified click type.
    """
    
    @property
    def action_type(self) -> str:
        return "click"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute click action"""
        coordinates = config.get('coordinates')
        if not coordinates or not isinstance(coordinates, (list, tuple)):
            return StepResult(self.action_type, False, error="Invalid coordinates")
            
        click_type = config.get('click_type', 'single')
        pre_delay = float(config.get('pre_delay', 0.1))
        post_delay = float(config.get('post_delay', 0.5))
        
        time.sleep(pre_delay)
        
        x, y = coordinates
        MouseController.move_to(x, y)
        time.sleep(0.1)
        
        if click_type == 'double':
            MouseController.click(x, y) # TODO: Implement double click in MouseController if needed or just click twice
            time.sleep(0.1)
            MouseController.click(x, y)
        elif click_type == 'right':
             # TODO: Implement right click support if needed
             MouseController.click(x, y) 
        else:
            MouseController.click(x, y)
            
        time.sleep(post_delay)
        
        return StepResult(self.action_type, True, data={'clicked_at': coordinates})

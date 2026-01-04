import time
from typing import Dict, Any
from . import BaseAction, StepResult
from automation import MouseController

class ClickAction(BaseAction):
    """
    Action to click mouse at specific coordinates.
    
    Inputs (Config):
        coordinates (list/tuple): [x, y] coordinates to click
        offset_x (int): Optional X offset from coordinates (default: 0)
        offset_y (int): Optional Y offset from coordinates (default: 0)
        click_type (str): 'single', 'double', 'right' (default: 'single')
        pre_delay (float): Wait before click (default: 0.1s)
        post_delay (float): Wait after click (default: 0.5s)
        
    Outputs (StepResult.data):
        clicked_at (tuple): The coordinates clicked
        
    Effect:
        Moves mouse cursor to {coordinates}+offset.
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
        
        # Support offset from coordinates
        offset_x = int(config.get('offset_x', 0))
        offset_y = int(config.get('offset_y', 0))
        
        time.sleep(pre_delay)
        
        x, y = coordinates
        x = int(x) + offset_x
        y = int(y) + offset_y
        
        MouseController.move_to(x, y)
        time.sleep(0.1)
        
        if click_type == 'double':
            MouseController.click(x, y)
            time.sleep(0.1)
            MouseController.click(x, y)
        elif click_type == 'right':
             MouseController.click(x, y) 
        else:
            MouseController.click(x, y)
            
        time.sleep(post_delay)
        
        return StepResult(self.action_type, True, data={'clicked_at': (x, y)})


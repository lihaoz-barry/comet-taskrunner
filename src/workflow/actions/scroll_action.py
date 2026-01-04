import logging
from typing import Dict, Any
from . import BaseAction, StepResult

logger = logging.getLogger(__name__)


class ScrollAction(BaseAction):
    """
    Action to perform mouse wheel scrolling at a specific position.
    
    Inputs (Config):
        direction (str): 'up' | 'down' (default: down)
        clicks (int): Number of scroll clicks (default: 3)
        position (str|dict): Position to scroll at:
            - "current": scroll at current mouse position
            - "relative": use reference_position + offset
            - {x, y}: specific coordinates
        reference_position (tuple|str): Reference coordinates for relative mode
        offset (dict): {x, y} offset from reference position (default: {x: 0, y: 10})
        
    Outputs (StepResult.data):
        scroll_position (tuple): The (x, y) position where scrolling occurred
        
    Effect:
        Moves mouse to position and performs scroll.
    """
    
    @property
    def action_type(self) -> str:
        return "scroll"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute scroll operation"""
        import pyautogui
        
        direction = config.get('direction', 'down')
        clicks = int(config.get('clicks', 3))
        position_mode = config.get('position', 'current')
        
        try:
            # Determine scroll position
            if position_mode == 'current':
                # Scroll at current mouse position
                scroll_x, scroll_y = pyautogui.position()
            elif position_mode == 'relative':
                # Use reference position + offset
                ref_pos = config.get('reference_position')
                offset = config.get('offset', {'x': 0, 'y': 10})
                
                # Resolve reference if it's a context key
                if isinstance(ref_pos, str) and ref_pos in context:
                    ref_pos = context[ref_pos]
                
                if ref_pos is None:
                    return StepResult(self.action_type, False, error="reference_position is required for relative mode")
                
                # Handle tuple or dict format
                if isinstance(ref_pos, (list, tuple)):
                    ref_x, ref_y = ref_pos[0], ref_pos[1]
                elif isinstance(ref_pos, dict):
                    ref_x, ref_y = ref_pos.get('x', 0), ref_pos.get('y', 0)
                else:
                    return StepResult(self.action_type, False, error=f"Invalid reference_position format: {type(ref_pos)}")
                
                offset_x = int(offset.get('x', 0))
                offset_y = int(offset.get('y', 10))
                
                scroll_x = int(ref_x) + offset_x
                scroll_y = int(ref_y) + offset_y
            elif isinstance(position_mode, dict):
                # Specific coordinates
                scroll_x = int(position_mode.get('x', 0))
                scroll_y = int(position_mode.get('y', 0))
            else:
                return StepResult(self.action_type, False, error=f"Unknown position mode: {position_mode}")
            
            # Move to position
            pyautogui.moveTo(scroll_x, scroll_y)
            
            # Perform scroll
            scroll_amount = -clicks if direction == 'down' else clicks
            pyautogui.scroll(scroll_amount)
            
            logger.info(f"Scrolled {direction} {clicks} clicks at ({scroll_x}, {scroll_y})")
            return StepResult(self.action_type, True, data={'scroll_position': (scroll_x, scroll_y)})
            
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            import traceback
            traceback.print_exc()
            return StepResult(self.action_type, False, error=str(e))

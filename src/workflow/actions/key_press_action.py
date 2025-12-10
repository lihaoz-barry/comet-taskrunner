import time
import logging
from typing import Dict, Any
from . import BaseAction, StepResult
from automation import MouseController

logger = logging.getLogger(__name__)

class KeyPressAction(BaseAction):
    """
    Action to simulate pressing a keyboard key.
    
    Inputs (Config):
        key (str): Key name (e.g., 'enter', 'tab', 'esc', 'a')
        post_delay (float): Delay after press (default: 0.5)
        text_context (str): Optional text content used for logic (e.g. check for slash commands)
        
    Outputs (StepResult.data):
        key (str): The key pressed
        repeat (int): How many times it was pressed
        
    Effect:
        Simulates pressing the specified key.
        Special Logic: If 'key' is 'enter' and 'text_context' starts with '/', 
        it presses enter twice (for slash commands).
    """
    
    @property
    def action_type(self) -> str:
        return "key_press"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute key press action"""
        key = config.get('key')
        post_delay = float(config.get('post_delay', 0.5))
        text_context = config.get('text_context')
        
        repeat = 1
        
        # Logic for smart enter (slash commands)
        if key == 'enter' and text_context and isinstance(text_context, str):
            if text_context.strip().startswith('/'):
                logger.info("Detected slash command, will press Enter twice")
                repeat = 2
        
        for i in range(repeat):
            MouseController.press_key(key)
            if i < repeat - 1:
                time.sleep(0.1)
                
        time.sleep(post_delay)
        
        return StepResult(self.action_type, True, data={'key': key, 'repeat': repeat})

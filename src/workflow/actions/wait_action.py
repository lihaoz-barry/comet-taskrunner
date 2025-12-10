import time
from typing import Dict, Any
from . import BaseAction, StepResult

class WaitAction(BaseAction):
    """
    Action to pause execution for a specific duration.
    
    Inputs (Config):
        duration (float): Time to wait in seconds (default: 1.0)
        description (str): Optional description for logging
        
    Outputs (StepResult.data):
        waited (float): The actual duration waited
        
    Effect:
        Blocks execution thread for 'duration' seconds.
    """
    
    @property
    def action_type(self) -> str:
        return "wait"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """
        Execute wait action.
        
        Args:
            config: {'duration': float, 'description': str}
            context: Workflow context
        """
        duration = float(config.get('duration', 1.0))
        description = config.get('description', 'Waiting')
        
        time.sleep(duration)
        
        return StepResult(self.action_type, True, data={'waited': duration})

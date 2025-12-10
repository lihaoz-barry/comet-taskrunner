import logging
from typing import Dict, Any
from . import BaseAction, StepResult

logger = logging.getLogger(__name__)

class CompletionAction(BaseAction):
    """
    Action to mark the workflow as completed.
    
    Inputs (Config):
        status (str): Final status (default 'success')
        message (str): Completion message
        
    Outputs (StepResult.data):
        final_status (str): The logged status
        message (str): The logged message
        
    Effect:
        Logs completion message.
        Acts as a clear signal that the workflow logic finished successfully.
    """
    
    @property
    def action_type(self) -> str:
        return "completion"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute completion action"""
        status = config.get('status', 'success')
        message = config.get('message', 'Workflow completed')
        
        logger.info(f"WORKFLOW COMPLETED: {status} - {message}")
        
        return StepResult(self.action_type, True, data={'final_status': status, 'message': message})

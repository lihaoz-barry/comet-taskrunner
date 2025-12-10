from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class StepResult:
    """Result of a single workflow step execution"""
    
    def __init__(self, step_name: str, success: bool, data: Dict[str, Any] = None, error: Optional[str] = None):
        self.step_name = step_name
        self.success = success
        self.data = data or {}
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_name": self.step_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }

class BaseAction(ABC):
    """Abstract base class for all workflow actions"""
    
    @abstractmethod
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """
        Execute the action.
        
        Args:
            config: Configuration dictionary for this action instance
            context: Execution context containing variables and previous step outputs
            
        Returns:
            StepResult object indicating success/failure and data
        """
        pass
    
    @property
    @abstractmethod
    def action_type(self) -> str:
        """Return the type identifier for this action (e.g., 'click', 'wait')"""
        pass

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

        # Extended fields (set by ConfigurableTask for history tracking)
        self.step_index: Optional[int] = None
        self.step_id: Optional[str] = None
        self.display_name: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.duration_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "step_name": self.step_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }

        # Include extended fields if set
        if self.step_index is not None:
            result["step_index"] = self.step_index
        if self.step_id is not None:
            result["step_id"] = self.step_id
        if self.display_name is not None:
            result["display_name"] = self.display_name
        if self.started_at is not None:
            result["started_at"] = self.started_at.isoformat()
        if self.completed_at is not None:
            result["completed_at"] = self.completed_at.isoformat()
        if self.duration_ms is not None:
            result["duration_ms"] = self.duration_ms

        return result

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

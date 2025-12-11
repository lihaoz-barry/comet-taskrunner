import threading
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base_task import BaseTask, TaskType, TaskResult, TaskStatus
from workflow import WorkflowConfig, StepExecutor, StepResult as WorkflowStepResult

logger = logging.getLogger(__name__)

class ConfigurableTask(BaseTask):
    """
    Generic task implementation driven by YAML configuration.
    
    This adapter class wraps the StepExecutor to make it compatible
    with the existing TaskRunner system (BaseTask).
    """
    
    def __init__(self, workflow_config: WorkflowConfig, inputs: Dict[str, Any]):
        super().__init__(TaskType.CUSTOM) # Or add a NEW type if needed
        self.workflow_config = workflow_config
        self.inputs = inputs
        self.executor = StepExecutor(workflow_config)
        self.executor.set_inputs(inputs)
        
        # Override task type if provided in mapping
        # For now, map 'ai_assistant' -> AI_ASSISTANT for backward compatibility if needed
        # But ideally we use dynamic types. 
        # BaseTask has an enum TaskType.CUSTOM which we can use.
        
        self.step_results = []
        self.execution_thread: Optional[threading.Thread] = None
        self.current_step_index = 0
        self.total_steps = len(workflow_config.steps)
        self.completed = False
        
    def execute(self, **kwargs) -> int:
        """
        Start workflow execution in a background thread.
        Returns a dummy process ID since we manage our own thread.
        """
        logger.info(f"Starting configurable task: {self.workflow_config.name}")
        
        self.execution_thread = threading.Thread(
            target=self._run_workflow,
            daemon=True
        )
        self.execution_thread.start()
        
        # Return a dummy PID (or current PID) since we don't necessarily spawn a process
        import os
        return os.getpid()

    def _run_workflow(self):
        """Execute all steps sequentially"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        
        try:
            for i, step in enumerate(self.workflow_config.steps):
                self.current_step_index = i + 1
                logger.info(f"Executing step {i+1}/{self.total_steps}: {step.name}")
                
                result = self.executor.execute_step(step)
                self.step_results.append(result)
                
                if not result.success:
                    error_msg = f"Step '{step.name}' failed: {result.error}"
                    self.fail(error_msg)
                    return
            
            # All steps finished
            self.completed = True
            self.complete()
            
        except Exception as e:
            self.fail(str(e))

    def check_completion(self) -> bool:
        """Check if workflow is finished"""
        return self.status in [TaskStatus.DONE, TaskStatus.FAILED]

    def get_progress(self) -> Dict[str, Any]:
        """Get standardized progress info"""
        
        status_text = "Initializing..."
        if self.step_results:
            last_result = self.step_results[-1]
            # Use display name if available in config, otherwise step name
            current_step_config = self.workflow_config.steps[len(self.step_results)-1]
            status_text = current_step_config.display_name or current_step_config.name
            
        progress_percent = int((len(self.step_results) / self.total_steps) * 100) if self.total_steps > 0 else 0
        
        return {
            'has_steps': True,
            'current_step': self.current_step_index,
            'total_steps': self.total_steps,
            'progress_percent': progress_percent,
            'status_text': status_text,
            'details': {
                'workflow_name': self.workflow_config.name,
                'current_step_id': self.workflow_config.steps[self.current_step_index-1].id if 0 < self.current_step_index <= len(self.workflow_config.steps) else None,
                'inputs': self.inputs
            }
        }

    def get_automation_progress(self) -> Dict[str, Any]:
        """
        Get progress in format expected by StatusOverlay.
        """
        return {
            'current_step': self.current_step_index,
            'total_steps': self.total_steps,
            'completed_steps': len(self.step_results),
            'progress_percent': int((len(self.step_results) / self.total_steps) * 100) if self.total_steps > 0 else 0
        }

    @property
    def STEP_DESCRIPTIONS(self) -> Dict[int, tuple]:
        """
        Generate step descriptions for the overlay from workflow config.
        Returns map of step_index -> (current_desc, next_desc)
        """
        descriptions = {}
        steps = self.workflow_config.steps
        
        for i, step in enumerate(steps):
            step_num = i + 1
            # Current step description
            current = step.display_name or step.name
            
            # Next step description
            if i + 1 < len(steps):
                next_step = steps[i+1]
                next_desc = next_step.display_name or next_step.name
            else:
                next_desc = "完成"
                
            descriptions[step_num] = (current, next_desc)
            
        return descriptions

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize task to dictionary.

        Adds workflow-specific fields including inputs.
        """
        data = super().to_dict()
        data['workflow_name'] = self.workflow_config.name
        data['inputs'] = self.inputs
        # Add instruction field for backward compatibility with frontend
        # (frontend expects 'instruction' for AI tasks)
        if 'instruction' in self.inputs:
            data['instruction'] = self.inputs['instruction']
        return data

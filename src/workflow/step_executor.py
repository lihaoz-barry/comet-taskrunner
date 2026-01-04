import logging
from typing import Dict, Any, Type, Optional
from .workflow_config import WorkflowConfig, StepConfig
from .actions import BaseAction, StepResult

logger = logging.getLogger(__name__)

class ActionRegistry:
    """Registry for available task actions"""
    _actions: Dict[str, Type[BaseAction]] = {}
    
    @classmethod
    def register(cls, action_class: Type[BaseAction]):
        """Register a new action class"""
        instance = action_class() # Create dummy instance to get type
        cls._actions[instance.action_type] = action_class
        logger.debug(f"Registered action: {instance.action_type}")
        
    @classmethod
    def get(cls, action_type: str) -> Optional[Type[BaseAction]]:
        return cls._actions.get(action_type)

class StepExecutor:
    """Executes workflow steps"""
    
    def __init__(self, workflow_config: WorkflowConfig):
        self.config = workflow_config
        self.context: Dict[str, Any] = {}
        
        # Initialize context with inputs
        self.context['inputs'] = {}
        self.current_step_logs = []  # Capture logs for current step
        
        # Resolve template directory
        import sys
        from pathlib import Path
        
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
        else:
            # Development mode: resolve relative to project root
            # Assuming step_executor.py is in src/workflow/
            base_path = Path(__file__).parent.parent.parent
            
        template_dir_name = workflow_config.template_dir or "templates"
        self.context['template_dir'] = base_path / template_dir_name
        logger.info(f"Resolved template dir: {self.context['template_dir']}")
        
    def set_inputs(self, inputs: Dict[str, Any]):
        """Set workflow input values"""
        self.context['inputs'] = inputs
        
    def log(self, message: str):
        """Add a log entry for the current step"""
        self.current_step_logs.append(message)
        # Emit distinct log for formatter if it's a structural update
        if "Step:" in message:
             logger.info(message)
        else:
             logger.info(f"  > {message}") # Indent details

    def execute_step(self, step: StepConfig) -> StepResult:
        """Execute a single workflow step"""
        self.current_step_logs = []  # Clear logs for new step
        # Emit "Step Start" signal for formatter
        logger.info(f"Step: {step.name}...") 
        import time
        import time
        
        action_type = step.action_config.action
        
        # Handle composite actions (format: "composite:action_name")
        if action_type.startswith('composite:'):
            composite_name = action_type.split(':', 1)[1]
            from .actions.composite_action import CompositeAction
            action_class = CompositeAction
            # Store composite name in config for the action
            step.action_config.config['_composite_name'] = composite_name
        else:
            action_class = ActionRegistry.get(action_type)
        
        if not action_class:
            error = f"Unknown action type: {action_type}"
            logger.error(error)
            return StepResult(step.name, False, error=error)
            
        try:
            # Resolve configuration variables
            resolved_config = self._resolve_config(step.action_config.config)
            
            # Universal pre_delay - applies to ALL actions
            pre_delay = float(resolved_config.pop('pre_delay', 0.0))
            if pre_delay > 0:
                logger.debug(f"Pre-delay: {pre_delay}s before {step.name}")
                time.sleep(pre_delay)
            
            # Execute action
            action = action_class()
            result = action.execute(resolved_config, self.context)
            
            # Universal post_delay - applies to ALL actions
            post_delay = float(resolved_config.pop('post_delay', 0.0) if 'post_delay' in step.action_config.config else 0.0)
            if post_delay > 0:
                logger.debug(f"Post-delay: {post_delay}s after {step.name}")
                time.sleep(post_delay)
            
            # Store outputs in context
            if result.success and step.action_config.outputs:
                for output_def in step.action_config.outputs:
                    output_name = output_def['name']
                    # output_type = output_def.get('type') # Not used yet
                    
                    if output_name in result.data:
                        context_key = f"{step.id}.{output_name}"
                        self.context[context_key] = result.data[output_name]
                        logger.debug(f"Stored output: {context_key} = {result.data[output_name]}")
            
            # Log Success
            if result.success:
                 logger.info(f"Step: {step.name} Completed")
            else:
                 logger.info(f"Step: {step.name} Failed")

            return result
            
        except Exception as e:
            error_msg = f"Error executing step {step.name}: {e}"
            self.log(error_msg)
            # Log Failure explicitly for formatter
            logger.info(f"Step: {step.name} Failed")
            
            import traceback
            traceback.print_exc()
            return StepResult(step.name, False, error=str(e))

    def _resolve_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deeply resolve references in configuration dict"""
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str) and self._is_reference(value):
                resolved[key] = self._resolve_value(value)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_config(value)
            else:
                resolved[key] = value
        return resolved
        
    def _is_reference(self, value: str) -> bool:
        """Check if string is a variable reference (simple check)"""
        # Supports: "inputs.var_name" or "step_id.output_name"
        # Must contain dot
        if "." not in value:
            return False
            
        # exclude paths (start with / or .)
        if value.startswith("/") or value.startswith("."):
            return False
            
        # exclude image files
        if value.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            return False
            
        # exclude registry keys or windows paths (contain backslash)
        if "\\" in value:
            return False
            
        # exclude strings with spaces (vars usually don't have spaces)
        if " " in value:
            return False
            
        return True

    def _resolve_value(self, ref: str) -> Any:
        """Resolve a variable reference from context"""
        parts = ref.split('.')
        
        # Special case: inputs
        if parts[0] == 'inputs':
            input_name = parts[1]
            return self.context.get('inputs', {}).get(input_name)
            
        # General case: step output
        # references are stored as "step_id.output_name" in self.context keys directly?
        # Actually in execute_step I stored them as f"{step.id}.{output_name}"
        # So "step_3.assistant_coords" matches the key exactly.
        
        if ref in self.context:
            return self.context[ref]
            
        logger.warning(f"Could not resolve reference: {ref}")
        return ref # Return original string if not found

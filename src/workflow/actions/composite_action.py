"""
Composite Action System

Allows defining reusable action sequences in YAML files.
These can be called from workflows using: action: "composite:action_name"
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from .base_action import BaseAction, StepResult

logger = logging.getLogger(__name__)


class CompositeActionConfig:
    """Configuration for a composite action loaded from YAML"""
    
    def __init__(self, name: str, description: str, inputs: list, steps: list, outputs: list):
        self.name = name
        self.description = description
        self.inputs = inputs  # List of input definitions
        self.steps = steps    # List of step definitions
        self.outputs = outputs  # List of output mappings
    
    @classmethod
    def from_yaml(cls, yaml_data: Dict) -> 'CompositeActionConfig':
        """Create CompositeActionConfig from parsed YAML data"""
        composite = yaml_data.get('composite_action', {})
        return cls(
            name=composite.get('name', 'unnamed'),
            description=composite.get('description', ''),
            inputs=yaml_data.get('inputs', []),
            steps=yaml_data.get('steps', []),
            outputs=yaml_data.get('outputs', [])
        )


class CompositeActionRegistry:
    """Registry for composite actions loaded from YAML files"""
    
    _actions: Dict[str, CompositeActionConfig] = {}
    
    @classmethod
    def load_from_directory(cls, directory: str):
        """Load all composite action YAML files from a directory"""
        path = Path(directory)
        if not path.exists():
            logger.warning(f"Composite actions directory not found: {directory}")
            return
        
        logger.info(f"Loading composite actions from: {directory}")
        
        files = list(path.glob('*.yaml')) + list(path.glob('*.yml'))
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                if 'composite_action' in data:
                    config = CompositeActionConfig.from_yaml(data)
                    cls._actions[config.name] = config
                    logger.info(f"Loaded composite action: {config.name}")
            except Exception as e:
                logger.error(f"Failed to load composite action {file_path.name}: {e}")
        
        logger.info(f"Loaded {len(cls._actions)} composite actions")
    
    @classmethod
    def get(cls, name: str) -> Optional[CompositeActionConfig]:
        """Get a composite action by name"""
        return cls._actions.get(name)
    
    @classmethod
    def list_actions(cls) -> list:
        """List all available composite actions"""
        return list(cls._actions.keys())


class CompositeAction(BaseAction):
    """
    Meta-action that executes a sequence of other actions.
    
    Usage in YAML:
        action: "composite:capture_copy"
        config:
            copy_button_template: "button.png"
    """
    
    def __init__(self, composite_name: str = None):
        self._composite_name = composite_name
    
    @property
    def action_type(self) -> str:
        return "composite"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute the composite action sequence"""
        from ..step_executor import ActionRegistry
        
        # Get composite action name (passed via composite_name in config or constructor)
        composite_name = config.pop('_composite_name', self._composite_name)
        
        if not composite_name:
            return StepResult(self.action_type, False, error="No composite action name specified")
        
        # Get the composite action config
        composite_config = CompositeActionRegistry.get(composite_name)
        
        if not composite_config:
            return StepResult(self.action_type, False, 
                            error=f"Composite action not found: {composite_name}")
        
        logger.info(f"Executing composite action: {composite_name}")
        
        # Create local context for this composite action
        local_context = dict(context)
        local_context['inputs'] = config  # User-provided config becomes inputs
        
        # Execute each step
        step_outputs = {}
        
        for step in composite_config.steps:
            step_id = step.get('id', 'unknown')
            action_name = step.get('action')
            step_config = step.get('config', {})
            step_outputs_def = step.get('outputs', [])
            
            # Resolve config references
            resolved_config = self._resolve_references(step_config, local_context, step_outputs)
            
            import time
            
            # Universal pre_delay
            pre_delay = float(resolved_config.pop('pre_delay', 0.0))
            if pre_delay > 0:
                time.sleep(pre_delay)
            
            # Get action class
            action_class = ActionRegistry.get(action_name)
            if not action_class:
                return StepResult(self.action_type, False, 
                                error=f"Unknown action in composite: {action_name}")
            
            # Execute action
            action = action_class()
            result = action.execute(resolved_config, local_context)
            
            # Universal post_delay
            post_delay = float(resolved_config.pop('post_delay', 0.0))
            if post_delay > 0:
                time.sleep(post_delay)
            
            if not result.success:
                return StepResult(self.action_type, False, 
                                error=f"Composite step '{step_id}' failed: {result.error}")
            
            # Store step outputs
            for output_def in step_outputs_def:
                output_name = output_def.get('name')
                if output_name and output_name in result.data:
                    step_outputs[f"{step_id}.{output_name}"] = result.data[output_name]
        
        # Map final outputs
        final_outputs = {}
        for output_def in composite_config.outputs:
            output_name = output_def.get('name')
            from_ref = output_def.get('from')
            if from_ref and from_ref in step_outputs:
                final_outputs[output_name] = step_outputs[from_ref]
        
        logger.info(f"Composite action '{composite_name}' completed successfully")
        return StepResult(self.action_type, True, data=final_outputs)
    
    def _resolve_references(self, config: Any, context: Dict, step_outputs: Dict) -> Any:
        """Resolve references in config values"""
        if isinstance(config, str):
            # Check for step output reference
            if config in step_outputs:
                return step_outputs[config]
            # Check for input reference
            if config.startswith('inputs.'):
                input_name = config.split('.', 1)[1]
                return context.get('inputs', {}).get(input_name, config)
            return config
        elif isinstance(config, dict):
            return {k: self._resolve_references(v, context, step_outputs) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_references(item, context, step_outputs) for item in config]
        return config

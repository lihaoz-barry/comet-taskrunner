import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ActionConfig:
    """Configuration for a specific action"""
    action: str
    config: Dict[str, Any]
    outputs: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class StepConfig:
    """Configuration for a single workflow step"""
    id: str
    name: str
    action_config: ActionConfig
    display_name: Optional[str] = None

@dataclass
class WorkflowConfig:
    """Complete workflow configuration"""
    name: str
    version: str
    description: str
    api_endpoint: str
    template_dir: str
    inputs: List[Dict[str, Any]]
    steps: List[StepConfig]
    error_handling: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

def load_workflow_from_yaml(file_path: str) -> WorkflowConfig:
    """Parse YAML file into WorkflowConfig object"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        # Parse workflow metadata
        wf_data = data.get('workflow', {})
        
        # Parse steps
        steps = []
        for step_data in data.get('steps', []):
            action_config = ActionConfig(
                action=step_data.get('action'),
                config=step_data.get('config', {}),
                outputs=step_data.get('outputs', [])
            )
            
            step = StepConfig(
                id=step_data.get('id'),
                name=step_data.get('name'),
                display_name=step_data.get('display_name'),
                action_config=action_config
            )
            steps.append(step)
            
        return WorkflowConfig(
            name=wf_data.get('name'),
            version=wf_data.get('version', '1.0.0'),
            description=wf_data.get('description', ''),
            api_endpoint=wf_data.get('api_endpoint'),
            template_dir=wf_data.get('template_dir'),
            inputs=wf_data.get('inputs', []),
            steps=steps,
            error_handling=data.get('error_handling', {}),
            metadata=data.get('metadata', {})
        )
        
    except Exception as e:
        logger.error(f"Failed to load workflow from {file_path}: {e}")
        raise

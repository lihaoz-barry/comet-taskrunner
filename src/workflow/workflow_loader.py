import logging
import os
from pathlib import Path
from typing import Dict, Optional, List
from .workflow_config import WorkflowConfig, load_workflow_from_yaml

logger = logging.getLogger(__name__)

class WorkflowRegistry:
    """Registry to manage available workflows"""
    
    def __init__(self, workflows_dir: Optional[str] = None):
        self._workflows_by_name: Dict[str, WorkflowConfig] = {}
        self._workflows_by_endpoint: Dict[str, WorkflowConfig] = {}
        
        if workflows_dir:
            self.load_from_directory(workflows_dir)
            
    def load_from_directory(self, directory: str):
        """Load all YAML workflows from a directory"""
        path = Path(directory)
        if not path.exists():
            logger.warning(f"Workflows directory not found: {directory}")
            return
            
        logger.info(f"Loading workflows from: {directory}")
        
        # Find all .yaml and .yml files
        files = list(path.glob('*.yaml')) + list(path.glob('*.yml'))
        
        for file_path in files:
            try:
                workflow = load_workflow_from_yaml(str(file_path))
                self.register(workflow)
                logger.debug(f"Loaded workflow: {workflow.name}")
            except Exception as e:
                logger.error(f"Failed to load workflow {file_path.name}: {e}")
                
        logger.info(f"Loaded {len(self._workflows_by_name)} workflows")

    def register(self, workflow: WorkflowConfig):
        """Register a single workflow configuration"""
        self._workflows_by_name[workflow.name] = workflow
        
        # Also index by API endpoint for routing
        if workflow.api_endpoint:
            # Strip leading slash for consistent matching
            endpoint = workflow.api_endpoint.strip('/')
            self._workflows_by_endpoint[endpoint] = workflow
            
    def get_by_name(self, name: str) -> Optional[WorkflowConfig]:
        """Get workflow by name"""
        return self._workflows_by_name.get(name)
        
    def get_by_endpoint(self, endpoint: str) -> Optional[WorkflowConfig]:
        """
        Get workflow by API endpoint
        
        Args:
            endpoint: URL path segment (e.g. 'execute/ai')
        """
        endpoint = endpoint.strip('/')
        return self._workflows_by_endpoint.get(endpoint)
        
    def list_workflows(self) -> List[Dict[str, str]]:
        """List all available workflows"""
        return [
            {
                "name": wf.name,
                "display_name": wf.metadata.get("display_name", wf.name), 
                "description": wf.description,
                "endpoint": wf.api_endpoint
            }
            for wf in self._workflows_by_name.values()
        ]

"""
Task Manager

This module manages task instances.
It's a lightweight orchestrator - the TASKS themselves are separate components.

Responsibility:
    - Store tasks in memory
    - Provide lookup/query methods  
    - Periodic monitoring
    
NOT responsible for:
    - Task execution logic (handled by Task components)
    - Completion detection (handled by Task components)
    - Framework integration (handled by backend.py)

This follows the Single Responsibility Principle.
"""

import logging
import time
from typing import Dict, Optional, List, Any
from tasks import BaseTask, URLTask, AITask, TaskStatus, TaskType

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Lightweight task storage and monitoring manager.
    
    This is a simple dictionary wrapper with convenience methods.
    All task logic is in the Task components themselves.
    
    Storage:
        tasks: Dict[str, BaseTask] - In-memory task storage
    """
    
    def __init__(self):
        """Initialize empty task storage."""
        self.tasks: Dict[str, BaseTask] = {}
        logger.info("TaskManager initialized")
    
    # ------------------------------------------------------------------------
    # Factory Methods (Create tasks)
    # ------------------------------------------------------------------------
    
    def create_url_task(self, url: str) -> URLTask:
        """
        Create and store a URL task.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            URLTask: The created task
        """
        task = URLTask(url)
        self.tasks[task.task_id] = task
        return task
    
    def create_ai_task(
        self,
        instruction: str,
        coordinates: Optional[Dict] = None
    ) -> AITask:
        """
        Create and store an AI task.
        
        Args:
            instruction: The AI instruction
            coordinates: Optional coordinate overrides
            
        Returns:
            AITask: The created task
        """
        task = AITask(instruction, coordinates)
        self.tasks[task.task_id] = task
        return task

    def create_configurable_task(
        self,
        workflow_config,
        inputs: Dict[str, Any]
    ) -> BaseTask:
        """
        Create and store a configurable workflow task.
        
        Args:
            workflow_config: WorkflowConfig object
            inputs: Input dictionary
            
        Returns:
            ConfigurableTask: The created task
        """
        # Import internally to avoid circular dependency if any
        from tasks import ConfigurableTask
        
        task = ConfigurableTask(workflow_config, inputs)
        self.tasks[task.task_id] = task
        return task
    
    # ------------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------------
    
    def get_task(self, task_id: str) -> Optional[BaseTask]:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: The task ID
            
        Returns:
            BaseTask or None
        """
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Dict]:
        """
        Get all tasks as dictionaries.
        
        Returns:
            Dict mapping task_id to task data
        """
        return {
            task_id: task.to_dict()
            for task_id, task in self.tasks.items()
        }
    
    def get_tasks_by_type(self, task_type: TaskType) -> List[BaseTask]:
        """
        Get all tasks of a specific type.
        
        Args:
            task_type: TaskType enum
            
        Returns:
            List of matching tasks
        """
        return [
            task for task in self.tasks.values()
            if task.task_type == task_type
        ]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[BaseTask]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: TaskStatus enum
            
        Returns:
            List of matching tasks
        """
        return [
            task for task in self.tasks.values()
            if task.status == status
        ]
    
    # ------------------------------------------------------------------------
    # Status Updates
    # ------------------------------------------------------------------------
    
    def update_task_status(self, task_id: str, status: str):
        """
        Update task status (typically via callback).
        
        Args:
            task_id: The task ID
            status: New status string ("done", "failed")
        """
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Cannot update non-existent task: {task_id}")
            return
        
        if status == "done":
            task.complete()
        elif status == "failed":
            task.fail("Marked as failed via callback")
    
    # ------------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------------
    
    def monitor_tasks(self):
        """
        Check all running tasks for completion.
        
        This calls each task's check_completion() method.
        Tasks auto-complete if their check returns True.
        
        Should be called periodically (e.g., every 5 seconds).
        """
        for task_id, task in list(self.tasks.items()):
            if task.status == TaskStatus.RUNNING:
                # Call task-specific completion check
                if task.check_completion():
                    logger.info(f"Auto-completing task {task_id}")
                    task.complete()
    
    # ------------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------------
    
    def remove_completed_tasks(self, older_than_seconds: int = 3600):
        """
        Remove old completed tasks to free memory.
        
        Args:
            older_than_seconds: Remove tasks older than this (default 1 hour)
        """
        import time
        from datetime import datetime
        
        now = datetime.now()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.DONE, TaskStatus.FAILED]:
                if task.completed_at:
                    age = (now - task.completed_at).total_seconds()
                    if age > older_than_seconds:
                        to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
            logger.info(f"Removed old task: {task_id}")
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old tasks")

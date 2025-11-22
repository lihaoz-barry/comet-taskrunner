"""
Base Task Abstract Component

This module defines the abstract base class for all task types.
It can be imported and extended in ANY Python project.

Design Pattern: Template Method Pattern
- Base class defines the skeleton (lifecycle management)
- Subclasses implement specific behavior (execute, check_completion)

Input/Output Contract:
    Input:  Task-specific parameters (url, instruction, etc.)
    Output: TaskResult object with status, data, errors

Reusability:
    This is a pure component - no dependencies on Flask, Tkinter, or any specific framework.
    It can be used in CLI tools, web services, desktop apps, etc.

Example:
    from tasks.base_task import BaseTask, TaskStatus
    
    class MyCustomTask(BaseTask):
        def execute(self, **kwargs):
            # Implement your logic
            return process_id
        
        def check_completion(self):
            # Implement your detection
            return is_done
"""

import uuid
import time
import psutil
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class TaskStatus(Enum):
    """Status enum for task execution lifecycle"""
    CREATED = "created"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class TaskType(Enum):
    """Type identifier for different task implementations"""
    URL = "url"
    AI_ASSISTANT = "ai"
    CUSTOM = "custom"  # For user-defined task types


class TaskResult:
    """
    Standard result object returned by tasks.
    
    This provides a consistent interface for all task types.
    """
    def __init__(self, success: bool, data: Dict[str, Any] = None, error: str = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


# ============================================================================
# ABSTRACT BASE TASK COMPONENT
# ============================================================================

class BaseTask(ABC):
    """
    Abstract base class for all task types.
    
    This is a **pure component** with NO external dependencies.
    
    Lifecycle:
        1. __init__()        → CREATED
        2. start(pid)        → RUNNING
        3. complete()        → DONE
        4. fail(error)       → FAILED
    
    Subclass Contract:
        Must implement:
        - execute(**kwargs) -> int: Execute the task and return process ID
        - check_completion() -> bool: Check if task is complete
    
    Attributes:
        task_id (str): Unique identifier (UUID)
        task_type (TaskType): Type of this task
        status (TaskStatus): Current execution status
        process_id (int): OS process ID (if applicable)
        process (psutil.Process): Process object for monitoring
        created_at (datetime): Creation timestamp
        started_at (datetime): Start timestamp
        completed_at (datetime): Completion timestamp
        error_message (str): Error details if failed
    """
    
    def __init__(self, task_type: TaskType):
        """
        Initialize base task.
        
        Args:
            task_type: The TaskType enum value
        """
        self.task_id: str = str(uuid.uuid4())
        self.task_type: TaskType = task_type
        self.status: TaskStatus = TaskStatus.CREATED
        self.process_id: Optional[int] = None
        self.process: Optional[psutil.Process] = None
        
        # Timestamps
        self.created_at: datetime = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
        # Error tracking
        self.error_message: Optional[str] = None
        
        logger.info(f"Created {task_type.value} task {self.task_id}")
    
    # ------------------------------------------------------------------------
    # Lifecycle Management (Template Methods)
    # ------------------------------------------------------------------------
    
    def start(self, process_id: int):
        """
        Start task execution with process ID.
        
        This is called AFTER execute() to mark the task as running.
        
        Args:
            process_id: The OS process ID
        """
        self.process_id = process_id
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        
        try:
            self.process = psutil.Process(process_id)
            logger.info(f"Task {self.task_id} started with PID {process_id}")
        except psutil.NoSuchProcess:
            logger.error(f"Process {process_id} not found for task {self.task_id}")
            self.fail("Process not found immediately after launch")
    
    def complete(self) -> TaskResult:
        """
        Mark task as successfully completed.
        
        Returns:
            TaskResult with success=True
        """
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        duration = (self.completed_at - self.started_at).total_seconds() if self.started_at else 0
        logger.info(f"Task {self.task_id} completed in {duration:.2f}s")
        
        return TaskResult(success=True, data={
            "task_id": self.task_id,
            "duration_seconds": duration
        })
    
    def fail(self, error_message: str) -> TaskResult:
        """
        Mark task as failed.
        
        Args:
            error_message: Description of failure
            
        Returns:
            TaskResult with success=False
        """
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
        logger.error(f"Task {self.task_id} failed: {error_message}")
        
        return TaskResult(success=False, error=error_message)
    
    # ------------------------------------------------------------------------
    # Process Monitoring
    # ------------------------------------------------------------------------
    
    def is_process_running(self) -> bool:
        """
        Check if the associated process is still running.
        
        Returns:
            True if process exists and is running
        """
        if not self.process:
            return False
        
        try:
            return self.process.is_running() and self.process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def get_process_info(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed process information.
        
        Returns:
            Dict with process details or None
        """
        if not self.process:
            return None
        
        try:
            return {
                "pid": self.process.pid,
                "name": self.process.name(),
                "status": self.process.status(),
                "cpu_percent": self.process.cpu_percent(),
                "memory_mb": round(self.process.memory_info().rss / 1024 / 1024, 2),
                "create_time": datetime.fromtimestamp(self.process.create_time()).isoformat()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    # ------------------------------------------------------------------------
    # Abstract Methods (Must be implemented by subclasses)
    # ------------------------------------------------------------------------
    
    @abstractmethod
    def execute(self, **kwargs) -> int:
        """
        Execute this task.
        
        This is the CORE method that defines what the task does.
        Each subclass implements its own logic.
        
        Args:
            **kwargs: Task-specific parameters
            
        Returns:
            int: Process ID of the launched process
            
        Raises:
            Exception: If execution fails
            
        Example:
            # In URLTask
            def execute(self, comet_path: str) -> int:
                process = subprocess.Popen([comet_path, self.url])
                return process.pid
        """
        pass
    
    @abstractmethod
    def check_completion(self) -> bool:
        """
        Check if this task has completed.
        
        This is called periodically to detect task completion.
        Each task type has different completion criteria.
        
        Returns:
            bool: True if task is complete, False if still running
            
        Example:
            # In URLTask
            def check_completion(self) -> bool:
                return not self.is_process_running()
            
            # In AITask
            def check_completion(self) -> bool:
                if not self.is_process_running():
                    return True
                return self._ai_detect_completion()
        """
        pass
    
    # ------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary for API responses or storage.
        
        Returns:
            Dict representation of the task
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "process_id": self.process_id,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "is_process_alive": self.is_process_running(),
            "process_info": self.get_process_info()
        }

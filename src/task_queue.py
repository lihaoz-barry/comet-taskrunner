"""
Task Queue Manager

Master queue system that ensures sequential task execution.
Only one task runs at a time, additional tasks are queued in FIFO order.

Architecture:
    - Queue: List of pending tasks waiting to execute
    - Current: The single task currently executing
    - Completed: Recent completed tasks (kept for UI display)

Thread-safe operation using locks.
"""

import logging
import threading
import time
from collections import deque
from typing import Optional, List, Dict, Any
from pathlib import Path

# Import task components
from tasks import BaseTask, TaskStatus, TaskType

logger = logging.getLogger(__name__)


class TaskQueue:
    """
    Master task queue manager.
    
    Ensures only one task executes at a time.
    Queues additional tasks in FIFO order.
    
    Attributes:
        queue: Pending tasks (FIFO)
        current_task: Currently executing task (None if idle)
        completed_tasks: Recently completed tasks (max 10 for UI)
        lock: Thread lock for queue operations
    """
    
    def __init__(self, comet_path: str):
        """
        Initialize task queue.
        
        Args:
            comet_path: Path to Comet browser executable
        """
        self.queue: deque = deque()  # Pending tasks
        self.current_task: Optional[BaseTask] = None
        self.completed_tasks: deque = deque(maxlen=10)  # Keep last 10
        self.lock = threading.Lock()
        self.comet_path = comet_path
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("TaskQueue initialized")
    
    # ========================================================================
    # TASK SUBMISSION
    # ========================================================================
    
    def submit(self, task: BaseTask) -> str:
        """
        Submit a task to the queue.
        
        If no task is currently running, start immediately.
        Otherwise, add to queue.
        
        Args:
            task: The task to execute
            
        Returns:
            str: Task ID
        """
        with self.lock:
            if self.current_task is None:
                # Queue is idle, start immediately
                logger.info(f"Queue idle, starting task {task.task_id} immediately")
                self._execute_task(task)
            else:
                # Queue busy, add to pending
                logger.info(f"Queue busy, adding task {task.task_id} to queue (position {len(self.queue) + 1})")
                self.queue.append(task)
            
            return task.task_id
    
    # ========================================================================
    # TASK EXECUTION
    # ========================================================================
    
    def _execute_task(self, task: BaseTask):
        """
        Execute a task (internal method, assumes lock is held).
        
        Args:
            task: Task to execute
        """
        self.current_task = task
        
        try:
            # Execute task and get process ID
            process_id = task.execute(comet_path=self.comet_path)
            task.start(process_id)
            logger.info(f"Task {task.task_id} started with PID {process_id}")
        except Exception as e:
            logger.error(f"Failed to execute task {task.task_id}: {e}")
            task.fail(str(e))
            # Move to completed immediately
            self.completed_tasks.append(self.current_task)
            self.current_task = None
            # Try to start next task
            self._start_next()
    
    def _start_next(self):
        """
        Start the next queued task (internal method, assumes lock is held).
        
        Called when current task completes.
        """
        if len(self.queue) > 0:
            next_task = self.queue.popleft()
            logger.info(f"Starting next queued task: {next_task.task_id}")
            self._execute_task(next_task)
        else:
            logger.info("Queue empty, entering idle state")
    
    # ========================================================================
    # MONITORING
    # ========================================================================
    
    def _monitor_loop(self):
        """
        Background monitoring thread.
        
        Periodically checks if current task has completed.
        If so, moves it to completed and starts next task.
        """
        logger.info("TaskQueue monitor thread started")
        
        loop_count = 0
        while self.monitoring:
            time.sleep(1)  # Check every second
            loop_count += 1
            
            with self.lock:
                # Log detailed status every 2 seconds
                if loop_count % 2 == 0:
                    logger.info("=" * 60)
                    logger.info("📊 TASK QUEUE STATUS")
                    logger.info("=" * 60)
                    
                    if self.current_task:
                        task_type = self.current_task.task_type.value
                        task_id = self.current_task.task_id[:8]
                        status = self.current_task.status.value
                        
                        # Get automation progress for AI tasks
                        progress_info = ""
                        if hasattr(self.current_task, 'get_automation_progress'):
                            prog = self.current_task.get_automation_progress()
                            progress_info = f" - Step {prog.get('current_step', 0)}/{prog.get('total_steps', 7)}"
                        
                        logger.info(f"→ CURRENT: [{task_type.upper()}] {task_id} - {status}{progress_info}")
                    else:
                        logger.info("→ CURRENT: <idle>")
                    
                    logger.info(f"📋 QUEUED: {len(self.queue)} task(s)")
                    for i, task in enumerate(list(self.queue)):
                        task_type = task.task_type.value
                        task_id = task.task_id[:8]
                        logger.info(f"   {i+1}. [{task_type.upper()}] {task_id}")
                    
                    logger.info(f"✓ COMPLETED: {len(self.completed_tasks)} task(s)")
                    for task in list(self.completed_tasks):
                        task_type = task.task_type.value
                        task_id = task.task_id[:8]
                        status = task.status.value
                        logger.info(f"   [{task_type.upper()}] {task_id} - {status}")
                    
                    logger.info("=" * 60)
                
                # Check if current task completed
                if self.current_task:
                    if self.current_task.check_completion():
                        logger.info(f"✅ Task {self.current_task.task_id} completed")
                        self.current_task.complete()
                        
                        # Move to completed
                        self.completed_tasks.append(self.current_task)
                        self.current_task = None
                        
                        # Start next task
                        self._start_next()
    
    # ========================================================================
    # STATUS QUERIES
    # ========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete queue status.
        
        This is the main API method for UI polling.
        
        Returns:
            Dict with:
                - current: Currently executing task (or None)
                - queued: List of pending tasks
                - completed: Recently completed tasks
                - stats: Queue statistics
        """
        with self.lock:
            status = {
                'current': self._task_to_dict(self.current_task) if self.current_task else None,
                'queued': [self._task_to_dict(task) for task in self.queue],
                'completed': [self._task_to_dict(task) for task in self.completed_tasks],
                'stats': {
                    'queue_length': len(self.queue),
                    'is_idle': self.current_task is None,
                    'total_completed': len(self.completed_tasks)
                }
            }
            
            return status
    
    def _task_to_dict(self, task: BaseTask) -> Dict[str, Any]:
        """
        Convert task to dictionary for API response.
        
        Args:
            task: Task to serialize
            
        Returns:
            Dict with task information
        """
        data = task.to_dict()
        
        # Add automation progress for AI tasks
        if task.task_type == TaskType.AI_ASSISTANT:
            data['automation_progress'] = task.get_automation_progress()
        
        return data
    
    def get_task(self, task_id: str) -> Optional[BaseTask]:
        """
        Find a task by ID (in any state).
        
        Args:
            task_id: Task ID to find
            
        Returns:
            Task or None
        """
        with self.lock:
            # Check current task
            if self.current_task and self.current_task.task_id == task_id:
                return self.current_task
            
            # Check queue
            for task in self.queue:
                if task.task_id == task_id:
                    return task
            
            # Check completed
            for task in self.completed_tasks:
                if task.task_id == task_id:
                    return task
            
            return None
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    def shutdown(self):
        """Stop monitoring thread and cleanup."""
        logger.info("TaskQueue shutting down")
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)

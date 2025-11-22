"""
URL Task Component

This is a **pure, reusable component** for URL navigation tasks.
Can be used in ANY Python project without modification.

Input Contract:
    url (str): The URL to navigate to
    
Output Contract:
    execute() returns: int (process ID)
    check_completion() returns: bool
    
Dependencies:
    - subprocess (Python stdlib)
    - psutil (for process monitoring)
    
No framework dependencies! Can be used in:
    - Flask web services
    - Django applications
    - CLI tools
    - Desktop applications
    - Jupyter notebooks
    - Other automation scripts

Example Usage (Standalone):
    ```python
    from tasks import URLTask
    
    # Create task
    task = URLTask(url="https://www.google.com")
    
    # Execute
    pid = task.execute(comet_path="path/to/comet.exe")
    task.start(pid)
    
    # Monitor
    while task.status == TaskStatus.RUNNING:
        if task.check_completion():
            result = task.complete()
            print(f"Done! {result.data}")
            break
        time.sleep(1)
    ```

Example Usage (In other project):
    ```python
    # In your Flask API
    from tasks import URLTask
    
    @app.route('/browse')
    def browse():
        task = URLTask(url=request.args.get('url'))
        pid = task.execute(comet_path=BROWSER_PATH)
        task.start(pid)
        return {"task_id": task.task_id}
    ```
"""

import subprocess
import logging
from typing import Dict, Any
from .base_task import BaseTask, TaskType

logger = logging.getLogger(__name__)


class URLTask(BaseTask):
    """
    URL Navigation Task Component.
    
    A self-contained component for browser URL navigation.
    
    Attributes:
        url (str): The URL to navigate to
    
    Completion Criteria:
        - Browser process exits
        - Manual callback (handled externally)
    """
    
    def __init__(self, url: str):
        """
        Create a URL navigation task.
        
        Args:
            url (str): The URL to open in browser
            
        Example:
            task = URLTask("https://example.com")
        """
        super().__init__(TaskType.URL)
        self.url = url
        logger.info(f"URLTask created for: {url}")
    
    def execute(self, comet_path: str) -> int:
        """
        Execute URL navigation by launching browser.
        
        This method is PURE - it only depends on:
        - comet_path parameter
        - self.url attribute
        
        Args:
            comet_path (str): Full path to comet.exe or browser executable
            
        Returns:
            int: Process ID of launched browser
            
        Raises:
            FileNotFoundError: If comet_path doesn't exist
            Exception: If subprocess launch fails
            
        Example:
            pid = task.execute(comet_path="C:/path/to/comet.exe")
            print(f"Browser launched with PID: {pid}")
        """
        logger.info(f"Launching browser for URL: {self.url}")
        
        try:
            # Launch browser with URL as argument
            process = subprocess.Popen([comet_path, self.url])
            
            logger.info(f"Browser process started with PID: {process.pid}")
            return process.pid
            
        except FileNotFoundError:
            error_msg = f"Browser not found at: {comet_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        except Exception as e:
            error_msg = f"Failed to launch browser: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def check_completion(self) -> bool:
        """
        Check if URL task has completed.
        
        For URLTask, completion is detected when:
        1. Browser process has exited
        2. (Future) Page load complete detection
        
        This method is PURE - no side effects, just a boolean check.
        
        Returns:
            bool: True if task is complete, False if still running
            
        Example:
            if task.check_completion():
                task.complete()
        """
        # Simple check: if process is no longer running, task is done
        if not self.is_process_running():
            logger.info(f"URLTask {self.task_id} - browser process exited")
            return True
        
        # Could add more sophisticated checks here:
        # - Page load complete detection
        # - Network activity monitoring
        # - DOM ready state check
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize task to dictionary.
        
        Adds URL-specific fields to base representation.
        
        Returns:
            Dict: Complete task state
        """
        data = super().to_dict()
        data['url'] = self.url
        return data


# ============================================================================
# HELPER FUNCTIONS (Optional convenience functions)
# ============================================================================

def create_and_execute_url_task(url: str, comet_path: str) -> URLTask:
    """
    Convenience function to create and execute a URL task in one call.
    
    This is a helper for simple use cases.
    
    Args:
        url: The URL to navigate to
        comet_path: Path to browser executable
        
    Returns:
        URLTask: The created and started task
        
    Example:
        task = create_and_execute_url_task(
            url="https://example.com",
            comet_path="C:/path/to/comet.exe"
        )
        # Task is already running
        print(task.task_id)
    """
    task = URLTask(url)
    pid = task.execute(comet_path=comet_path)
    task.start(pid)
    return task

"""
AI Assistant Task Component

This is a **reusable component** for AI Assistant automation.
Can be used in ANY Python project.

Input Contract:
    instruction (str): The text instruction for AI
    coordinates (dict, optional): UI element coordinates
    
Output Contract:
    execute() returns: int (process ID)
    check_completion() returns: bool
    
Dependencies:
    - subprocess (stdlib)
    - threading (stdlib)
    - time (stdlib)
    - psutil
    - TODO: pyautogui (for mouse/keyboard)
    - TODO: PIL (for screenshots)
    - TODO: opencv/AI model (for detection)
    
Usage in Other Projects:
    ```python
    from tasks import AITask
    
    # In a Django view
    task = AITask(instruction="Summarize this document")
    pid = task.execute(comet_path=settings.BROWSER_PATH)
    task.start(pid)
    
    # Store task_id in session/database for later tracking
    request.session['ai_task_id'] = task.task_id
    ```
    
    ```python
    # In a CLI tool
    from tasks import AITask
    import time
    
    task = AITask("Generate report for Q4")
    pid = task.execute(comet_path="/usr/bin/comet")
    task.start(pid)
    
    # Simple polling
    while not task.check_completion():
        time.sleep(5)
    task.complete()
    ```

Component Philosophy:
    This component is SEPARATE from any framework.
    It defines WHAT to do, not WHERE/WHEN/HOW to integrate it.
    Integration is handled by the calling code (Flask, Django, etc.)
"""

import subprocess
import threading
import time
import logging
from typing import Dict, Any, Optional, Tuple
from .base_task import BaseTask, TaskType

logger = logging.getLogger(__name__)


class AITask(BaseTask):
    """
    AI Assistant Interaction Task Component.
    
    Automates interaction with AI assistant through:
    - Mouse clicks (coordinates)
    - Keyboard input (typing)
    - AI-based completion detection
    
    This is a PURE component - no Flask/Tkinter dependencies.
    
    Attributes:
        instruction (str): Text to send to AI
        coordinates (dict): UI element positions
    
    Completion Criteria:
        - Process exit
        - AI screenshot analysis (PLACEHOLDER)
        - Pattern matching (PLACEHOLDER)
    """
    
    # Default coordinates (can be overridden per instance)
    DEFAULT_COORDINATES = {
        'assistant_button': (100, 100),
        'task_input_box': (500, 300),
        'send_button': (800, 500)
    }
    
    def __init__(
        self,
        instruction: str,
        coordinates: Optional[Dict[str, Tuple[int, int]]] = None
    ):
        """
        Create an AI Assistant interaction task.
        
        Args:
            instruction: The text instruction for the AI
            coordinates: Optional coordinate overrides
                {
                    'assistant_button': (x, y),
                    'task_input_box': (x, y),
                    'send_button': (x, y)
                }
        
        Example:
            # Use default coordinates
            task = AITask("Summarize this document")
            
            # Use custom coordinates
            task = AITask(
                instruction="Generate report",
                coordinates={
                    'assistant_button': (200, 150),
                    'task_input_box': (600, 400),
                }
            )
        """
        super().__init__(TaskType.AI_ASSISTANT)
        self.instruction = instruction
        self.coordinates = coordinates or self.DEFAULT_COORDINATES.copy()
        
        logger.info(f"AITask created: {instruction[:50]}...")
    
    def execute(self, comet_path: str) -> int:
        """
        Execute AI automation sequence.
        
        Steps:
        1. Launch browser
        2. Wait for initialization
        3. Run automation sequence (background thread)
        4. Return process ID
        
        Args:
            comet_path: Path to browser executable
            
        Returns:
            int: Process ID of launched browser
            
        Raises:
            Exception: If browser launch fails
            
        Note:
            Automation runs in background thread to avoid blocking.
            The main thread returns immediately after launching.
        """
        logger.info("Launching browser for AI Assistant task")
        
        try:
            # Step 1: Launch browser (no URL, just open app)
            process = subprocess.Popen([comet_path])
            process_id = process.pid
            
            # Step 2 & 3: Schedule automation sequence
            automation_thread = threading.Thread(
                target=self._automation_sequence,
                daemon=True
            )
            automation_thread.start()
            
            logger.info(f"AI task browser started with PID: {process_id}")
            return process_id
            
        except Exception as e:
            error_msg = f"Failed to launch browser for AI task: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _automation_sequence(self):
        """
        Execute the automation sequence.
        
        This runs in a BACKGROUND THREAD to not block the API response.
        
        Sequence:
        1. Wait for browser initialization (3 seconds)
        2. Click AI Assistant button
        3. Click task input box
        4. Type instruction
        5. Send instruction
        
        Error Handling:
            Catches all exceptions and marks task as failed.
        """
        try:
            # Step 1: Wait for browser to fully load
            time.sleep(3)
            
            logger.info(f"Starting automation for task {self.task_id}")
            
            # Step 2: Click AI Assistant button
            self._click_assistant_button()
            time.sleep(0.5)
            
            # Step 3: Click input box
            self._click_task_input()
            time.sleep(0.5)
            
            # Step 4: Type instruction
            self._type_instruction()
            time.sleep(0.5)
            
            # Step 5: Send
            self._send_instruction()
            
            logger.info(f"Automation sequence completed for task {self.task_id}")
            
        except Exception as e:
            error_msg = f"Automation failed: {e}"
            logger.error(f"Task {self.task_id} - {error_msg}")
            self.fail(error_msg)
    
    # ------------------------------------------------------------------------
    # Automation Actions (PLACEHOLDERS - To be implemented)
    # ------------------------------------------------------------------------
    
    def _click_assistant_button(self):
        """
        PLACEHOLDER: Click the AI Assistant button.
        
        Implementation:
            import pyautogui
            x, y = self.coordinates['assistant_button']
            pyautogui.click(x, y)
        
        Alternative (more reliable):
            Use win32gui to find window by title/class
            Then calculate relative coordinates
        """
        x, y = self.coordinates['assistant_button']
        logger.info(f"[PLACEHOLDER] Click AI button at ({x}, {y})")
        
        # TODO: Implement
        # import pyautogui
        # pyautogui.click(x, y)
    
    def _click_task_input(self):
        """
        PLACEHOLDER: Click the task input box.
        
        Implementation:
            import pyautogui
            x, y = self.coordinates['task_input_box']
            pyautogui.click(x, y)
        """
        x, y = self.coordinates['task_input_box']
        logger.info(f"[PLACEHOLDER] Click input box at ({x}, {y})")
        
        # TODO: Implement
        # import pyautogui
        # pyautogui.click(x, y)
    
    def _type_instruction(self):
        """
        PLACEHOLDER: Type the instruction text.
        
        Implementation:
            import pyautogui
            pyautogui.write(self.instruction, interval=0.05)
        
        Alternative (faster):
            import pyperclip
            import pyautogui
            pyperclip.copy(self.instruction)
            pyautogui.hotkey('ctrl', 'v')
        """
        logger.info(f"[PLACEHOLDER] Type: {self.instruction[:50]}...")
        
        # TODO: Implement
        # import pyautogui
        # pyautogui.write(self.instruction, interval=0.05)
    
    def _send_instruction(self):
        """
        PLACEHOLDER: Send the instruction.
        
        Implementation (Option 1 - Click button):
            import pyautogui
            x, y = self.coordinates['send_button']
            pyautogui.click(x, y)
        
        Implementation (Option 2 - Press key - RECOMMENDED):
            import pyautogui
            pyautogui.press('enter')
        """
        logger.info("[PLACEHOLDER] Send instruction (Enter key)")
        
        # TODO: Implement (Option 2 is more reliable)
        # import pyautogui
        # pyautogui.press('enter')
    
    # ------------------------------------------------------------------------
    # Completion Detection
    # ------------------------------------------------------------------------
    
    def check_completion(self) -> bool:
        """
        Check if AI task has completed.
        
        Multi-level detection:
        1. Process exit (simple fallback)
        2. AI screenshot analysis (PLACEHOLDER)
        
        Returns:
            bool: True if task is complete
        """
        # Level 1: Process exit
        if not self.is_process_running():
            logger.info(f"AITask {self.task_id} - process exited")
            return True
        
        # Level 2: AI detection (PLACEHOLDER)
        # if self._ai_detect_completion():
        #     logger.info(f"AITask {self.task_id} - AI detected completion")
        #     return True
        
        return False
    
    def _ai_detect_completion(self) -> bool:
        """
        PLACEHOLDER: AI-based completion detection.
        
        Implementation Steps:
        1. Capture screenshot
        2. Analyze with AI/CV
        3. Return True if "done" pattern found
        
        Returns:
            bool: True if AI detected completion
        """
        logger.debug(f"[PLACEHOLDER] AI detection for task {self.task_id}")
        
        # TODO: Implement
        # screenshot = self._capture_screenshot()
        # result = ai_model.predict(screenshot)
        # return result.is_complete
        
        return False
    
    def _capture_screenshot(self):
        """
        PLACEHOLDER: Capture browser window screenshot.
        
        Implementation:
            import win32gui
            import win32ui
            from PIL import Image
            
            # Find window by PID
            hwnd = self._find_window_by_pid(self.process_id)
            # Capture window content
            screenshot = ...
            return screenshot
        
        Returns:
            PIL.Image or None
        """
        logger.debug("[PLACEHOLDER] Capture screenshot")
        
        # TODO: Implement
        pass
    
    # ------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize task to dictionary.
        
        Adds AI-specific fields to base representation.
        """
        data = super().to_dict()
        data['instruction'] = self.instruction
        data['coordinates'] = self.coordinates
        return data


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_and_execute_ai_task(
    instruction: str,
    comet_path: str,
    coordinates: Optional[Dict] = None
) -> AITask:
    """
    Convenience function to create and execute AI task.
    
    Args:
        instruction: The AI instruction
        comet_path: Path to browser
        coordinates: Optional coordinate overrides
        
    Returns:
        AITask: The created and started task
        
    Example:
        task = create_and_execute_ai_task(
            instruction="Summarize this document",
            comet_path="C:/path/to/comet.exe"
        )
        print(f"Task started: {task.task_id}")
    """
    task = AITask(instruction, coordinates)
    pid = task.execute(comet_path=comet_path)
    task.start(pid)
    return task

"""
AI Assistant Task Component - WITH OPENCV AUTOMATION

Fully automated AI interaction using:
- Window detection & activation
- OpenCV template matching
- MSS screenshot capture
- PyAutoGUI mouse/keyboard control

Input Contract:
    instruction (str): The text instruction for AI
    
Output Contract:
    execute() returns: int (process ID)
    check_completion() returns: bool
    get_automation_progress() returns: dict (step progress)
"""

import subprocess
import threading
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from .base_task import BaseTask, TaskType, TaskResult

# Import automation modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from automation import WindowManager, ScreenshotCapture, PatternMatcher, MouseController

logger = logging.getLogger(__name__)


class StepResult:
    """Result of a single automation step"""
    
    def __init__(self, step_name: str, success: bool, data: Dict = None, error: str = None):
        self.step_name = step_name
        self.success = success
        self.data = data or {}
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_name": self.step_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class AITask(BaseTask):
    """
    AI Assistant Interaction Task with OpenCV Automation.
    
    9-Step Automation Sequence:
    1. Launch Comet browser
    2. Activate window (force focus)
    3. Find Assistant button (template matching)
    4. Click Assistant button
    5. Find input box (template matching)
    6. Input prompt text
    7. Send instruction (Enter key)
    8. Periodic stop logo detection (every 2 seconds)
    9. Completion handler
    """
    
    # Template files (just filenames, path is in template_dir)
    TEMPLATES = {
        'assistant_button': 'comet_Assistant_Unactive.png',
        'input_box': 'comet_input_box.png',  # User needs to create this
        'stop_logo': 'comet_stop_logo.png',  # Stop detection logo
    }
    
    # Matching thresholds
    THRESHOLDS = {
        'assistant_button': 0.3,  # Fuzzy matching
        'input_box': 0.5,  # More strict
        'stop_logo': 0.7,  # Higher threshold for accurate stop detection
    }
    
    def __init__(self, instruction: str, template_dir: str = None):
        """
        Create AI automation task.
        
        Args:
            instruction: The text instruction for AI
            template_dir: Optional custom template directory
        """
        super().__init__(TaskType.AI_ASSISTANT)
        self.instruction = instruction
        
        # Template directory - support both dev mode and PyInstaller exe
        if template_dir:
            self.template_dir = Path(template_dir)
        else:
            # Check if running as PyInstaller bundle
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller exe - use _MEIPASS
                base_path = Path(sys._MEIPASS)
                self.template_dir = base_path / "templates"
                logger.info(f"Running as packaged exe, using _MEIPASS: {base_path}")
            else:
                # Running in development mode - use relative path
                self.template_dir = Path(__file__).parent.parent.parent / "templates"
        
        # Screenshot directory - always use current working directory
        # (not inside temp directory for PyInstaller)
        if getattr(sys, 'frozen', False):
            # For exe, use directory where exe is located
            exe_dir = Path(sys.executable).parent
            self.screenshot_dir = exe_dir / "screenshots"
        else:
            # For development, use project root
            self.screenshot_dir = Path(__file__).parent.parent.parent / "screenshots"
        
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # Automation state
        self.hwnd = None
        self.window_rect = None
        self.step_results = []
        
        # Track automation completion (not just process)
        self.automation_completed = False
        
        logger.info(f"AITask created with instruction: {instruction[:50]}...")
        logger.info(f"Template directory: {self.template_dir}")
        logger.info(f"Screenshot directory: {self.screenshot_dir}")
        
        # Verify template directory exists
        if not self.template_dir.exists():
            logger.error(f"Template directory not found: {self.template_dir}")
            logger.error("Please ensure templates folder is in the correct location")
        else:
            logger.info(f"✓ Template directory verified: {self.template_dir}")
    
    def execute(self, comet_path: str) -> int:
        """
        Execute AI automation sequence.
        
        Args:
            comet_path: Path to Comet browser executable
            
        Returns:
            int: Process ID
        """
        logger.info("="*60)
        logger.info("LAUNCHING COMET BROWSER FOR AI TASK")
        logger.info("="*60)
        
        try:
            # Launch browser
            process = subprocess.Popen([comet_path])
            process_id = process.pid
            
            logger.info(f"✓ Browser launched successfully, PID={process_id}")
            
            # Start automation in background thread
            automation_thread = threading.Thread(
                target=self._automation_sequence,
                daemon=True
            )
            automation_thread.start()
            
            return process_id
            
        except Exception as e:
            error_msg = f"Failed to launch browser: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _automation_sequence(self):
        """
        MAIN AUTOMATION SEQUENCE - 9 Steps
        
        Runs in background thread.
        """
        logger.info("="*60)
        logger.info("STARTING AUTOMATION SEQUENCE")
        logger.info(f"Task ID: {self.task_id}")
        logger.info(f"Instruction: {self.instruction}")
        logger.info("="*60)
        
        try:
            # Step 1: Wait for browser initialization
            self._step_1_wait_for_initialization()
            
            # Step 2: Activate window
            result = self._step_2_activate_window()
            if not result.success:
                self.fail(f"Step 2 failed: {result.error}")
                return
            
            # Step 3: Find Assistant button
            result = self._step_3_find_assistant()
            if not result.success:
                self.fail(f"Step 3 failed: {result.error}")
                return
            assistant_coords = result.data['coordinates']
            
            # Step 4: Click Assistant button
            result = self._step_4_click_assistant(assistant_coords)
            if not result.success:
                self.fail(f"Step 4 failed: {result.error}")
                return
            
            # Step 5: Find input box
            result = self._step_5_find_input_box()
            if not result.success:
                self.fail(f"Step 5 failed: {result.error}")
                return
            input_coords = result.data['coordinates']
            
            # Step 6: Input text
            result = self._step_6_input_text(input_coords)
            if not result.success:
                self.fail(f"Step 6 failed: {result.error}")
                return
            
            # Step 7: Send instruction
            result = self._step_7_send()
            if not result.success:
                self.fail(f"Step 7 failed: {result.error}")
                return
            
            # Step 8: Detect stop logo
            result = self._step_8_detect_stop_logo()
            if not result.success:
                self.fail(f"Step 8 failed: {result.error}")
                return
            
            # Step 9: Handle completion
            result = self._step_9_handle_completion()
            if not result.success:
                self.fail(f"Step 9 failed: {result.error}")
                return
            
            logger.info("="*60)
            logger.info("✓ AUTOMATION SEQUENCE COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            
            # Mark automation as completed
            self.automation_completed = True
            
        except Exception as e:
            error_msg = f"Automation sequence failed: {e}"
            logger.error(f"✗ {error_msg}")
            import traceback
            traceback.print_exc()
            self.fail(error_msg)
            # Mark automation as completed (even if failed)
            self.automation_completed = True
    
    # ========================================================================
    # AUTOMATION STEPS
    # ========================================================================
    
    def _step_1_wait_for_initialization(self):
        """Step 1: Wait for browser to initialize"""
        logger.info("")
        logger.info("[STEP 1/9] Waiting for browser initialization...")
        
        time.sleep(8)  # Give Comet more time to start (increased from 5s)
        
        result = StepResult("wait_initialization", True, 
                          data={'wait_time': 8})
        self.step_results.append(result)
        
        logger.info("  ✓ Browser initialization wait completed")
    
    def _step_2_activate_window(self) -> StepResult:
        """Step 2: Find and activate Comet window"""
        logger.info("")
        logger.info("[STEP 2/9] Activating Comet window...")
        
        try:
            # Find window - with filtering to exclude frontend
            logger.info("  → Searching for Comet browser window (excluding frontend)...")
            
            # Use more specific keywords to find actual browser, not frontend
            result = WindowManager.find_comet_window(keywords=["New Tab - Comet", "Comet"])
            
            # If found, verify it's not the frontend
            if result:
                hwnd, rect = result
                import win32gui
                window_title = win32gui.GetWindowText(hwnd)
                
                # Exclude frontend window
                if "Task Runner" in window_title:
                    logger.warning(f"  ⚠ Found frontend window, searching for browser window...")
                    # Try again without generic "Comet" keyword
                    result = WindowManager.find_comet_window(keywords=["New Tab"])
            
            if not result:
                error = "Comet browser windownot found (may still be loading)"
                logger.error(f"  ✗ {error}")
                logger.info("  💡 Tip: Browser may need more time to start")
                step_result = StepResult("activate_window", False, error=error)
                self.step_results.append(step_result)
                return step_result
            
            self.hwnd, self.window_rect = result
            window_title = win32gui.GetWindowText(self.hwnd)
            logger.info(f"  ✓ Window found: HWND={self.hwnd}, Title='{window_title}'")
            logger.info(f"  ✓ Window rect: {self.window_rect}")
            
            # Activate window
            success = WindowManager.activate_window(self.hwnd)
            
            if success:
                logger.info("  ✓ Window activated and focused")
                step_result = StepResult("activate_window", True,
                                          data={'hwnd': self.hwnd, 'rect': self.window_rect})
            else:
                logger.warning("  ⚠ Window activation may have failed, continuing...")
                step_result = StepResult("activate_window", True,  # Continue anyway
                                      data={'hwnd': self.hwnd, 'rect': self.window_rect})
            
            self.step_results.append(step_result)
            return step_result
            
        except Exception as e:
            error = f"Window activation error: {e}"
            logger.error(f"  ✗ {error}")
            step_result = StepResult("activate_window", False, error=error)
            self.step_results.append(step_result)
            return step_result
    
    def _step_3_find_assistant(self) -> StepResult:
        """Step 3: Find Assistant button using template matching"""
        logger.info("")
        logger.info("[STEP 3/9] Finding Assistant button...")
        
        try:
            # Refresh window position before screenshot
            if not self._refresh_window_position():
                return StepResult("find_assistant", False, 
                                error="Window position refresh failed")
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.screenshot_dir / f"assistant_button_{timestamp}.png"
            
            logger.info("  → Taking screenshot...")
            screenshot = ScreenshotCapture.capture_window(self.window_rect, str(screenshot_path))
            logger.info(f"  ✓ Screenshot saved: {screenshot_path.name}")
            
            # Template matching
            template_path = self.template_dir / self.TEMPLATES['assistant_button']
            threshold = self.THRESHOLDS['assistant_button']
            
            logger.info(f"  → Matching template: {template_path.name} (threshold={threshold})")
            
            coordinates = PatternMatcher.find_pattern(
                str(screenshot_path),
                str(template_path),
                self.window_rect,
                threshold
            )
            
            if coordinates:
                logger.info(f"  ✓ Assistant button found at: {coordinates}")
                step_result = StepResult("find_assistant", True,
                                      data={'coordinates': coordinates, 'confidence': 'matched'})
            else:
                error = "Assistant button not found in screenshot"
                logger.error(f"  ✗ {error}")
                step_result = StepResult("find_assistant", False, error=error)
            
            self.step_results.append(step_result)
            return step_result
            
        except Exception as e:
            error = f"Assistant button detection error: {e}"
            logger.error(f"  ✗ {error}")
            step_result = StepResult("find_assistant", False, error=error)
            self.step_results.append(step_result)
            return step_result
    
    def _step_4_click_assistant(self, coordinates: tuple) -> StepResult:
        """Step 4: Click Assistant button"""
        logger.info("")
        logger.info("[STEP 4/9] Clicking Assistant button...")
        
        try:
            x, y = coordinates
            logger.info(f"  → Moving mouse to ({x}, {y})...")
            
            MouseController.move_to(x, y, duration=0.5)
            time.sleep(0.2)
            
            logger.info("  → Clicking...")
            MouseController.click()
            
            logger.info("  ✓ Assistant button clicked")
            time.sleep(1)  # Wait for UI transition
            
            step_result = StepResult("click_assistant", True,
                                   data={'clicked_at': coordinates})
            self.step_results.append(step_result)
            return step_result
            
        except Exception as e:
            error = f"Click error: {e}"
            logger.error(f"  ✗ {error}")
            step_result = StepResult("click_assistant", False, error=error)
            self.step_results.append(step_result)
            return step_result
    
    def _step_5_find_input_box(self) -> StepResult:
        """Step 5: Find input box using template matching"""
        logger.info("")
        logger.info("[STEP 5/9] Finding input box...")
        
        try:
            # Refresh window position before screenshot
            if not self._refresh_window_position():
                return StepResult("find_input_box", False,
                                error="Window position refresh failed")
            
            # Take new screenshot (UI has changed after clicking Assistant)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.screenshot_dir / f"input_box_{timestamp}.png"
            
            logger.info("  → Taking screenshot...")
            time.sleep(0.5)  # Wait for UI to settle
            screenshot = ScreenshotCapture.capture_window(self.window_rect, str(screenshot_path))
            logger.info(f"  ✓ Screenshot saved: {screenshot_path.name}")
            
            # Template matching
            template_path = self.template_dir / self.TEMPLATES['input_box']
            
            # Check if template exists
            if not template_path.exists():
                logger.warning(f"  ⚠ Template not found: {template_path}")
                logger.warning("  ⚠ Skipping input box detection, using click position")
                # Fallback: click at center of window
                left, top, right, bottom = self.window_rect
                center_x = (left + right) // 2
                center_y = (top + bottom) // 2
                coordinates = (center_x, center_y)
                
                step_result = StepResult("find_input_box", True,
                                      data={'coordinates': coordinates, 'method': 'fallback'})
                self.step_results.append(step_result)
                return step_result
            
            threshold = self.THRESHOLDS['input_box']
            
            logger.info(f"  → Matching template: {template_path.name} (threshold={threshold})")
            
            coordinates = PatternMatcher.find_pattern(
                str(screenshot_path),
                str(template_path),
                self.window_rect,
                threshold
            )
            
            if coordinates:
                logger.info(f"  ✓ Input box found at: {coordinates}")
                step_result = StepResult("find_input_box", True,
                                      data={'coordinates': coordinates, 'method': 'template'})
            else:
                # Fallback to center
                logger.warning("  ⚠ Input box not found, using window center")
                left, top, right, bottom = self.window_rect
                center_x = (left + right) // 2
                center_y = (top + bottom) // 2 + 100  # Slightly below center
                coordinates = (center_x, center_y)
                
                step_result = StepResult("find_input_box", True,
                                      data={'coordinates': coordinates, 'method': 'fallback'})
            
            self.step_results.append(step_result)
            return step_result
            
        except Exception as e:
            error = f"Input box detection error: {e}"
            logger.error(f"  ✗ {error}")
            step_result = StepResult("find_input_box", False, error=error)
            self.step_results.append(step_result)
            return step_result
    
    def _step_6_input_text(self, coordinates: tuple) -> StepResult:
        """Step 6: Click input box and type prompt"""
        logger.info("")
        logger.info("[STEP 6/9] Inputting prompt text...")
        
        try:
            x, y = coordinates
            logger.info(f"  → Clicking input box at ({x}, {y})...")
            
            MouseController.click(x, y)
            time.sleep(0.3)
            
            # Type text
            logger.info(f"  → Typing text (length={len(self.instruction)})...")
            logger.info(f"  → Text: {self.instruction[:50]}...")
            
            MouseController.type_text(self.instruction, interval=0.05)
            
            logger.info("  ✓ Text input completed")
            time.sleep(0.5)
            
            step_result = StepResult("input_text", True,
                                   data={'text_length': len(self.instruction)})
            self.step_results.append(step_result)
            return step_result
            
        except Exception as e:
            error = f"Text input error: {e}"
            logger.error(f"  ✗ {error}")
            step_result = StepResult("input_text", False, error=error)
            self.step_results.append(step_result)
            return step_result
    
    def _step_7_send(self) -> StepResult:
        """Step 7: Send instruction (press Enter)"""
        logger.info("")
        logger.info("[STEP 7/9] Sending instruction...")
        
        try:
            # Check if prompt starts with "/" (slash command)
            is_slash_command = self.instruction.strip().startswith('/')
            
            if is_slash_command:
                logger.info("  → Detected slash command, pressing Enter twice...")
                MouseController.press_key('enter')
                time.sleep(0.1)  # Small delay between presses
                MouseController.press_key('enter')
                logger.info("  ✓ Slash command sent (double Enter)")
            else:
                logger.info("  → Pressing Enter key...")
                MouseController.press_key('enter')
                logger.info("  ✓ Instruction sent")
            
            time.sleep(0.5)
            
            step_result = StepResult("send_instruction", True, 
                                    data={'slash_command': is_slash_command})
            self.step_results.append(step_result)
            return step_result
            
        except Exception as e:
            error = f"Send error: {e}"
            logger.error(f"  ✗ {error}")
            step_result = StepResult("send_instruction", False, error=error)
            self.step_results.append(step_result)
            return step_result
    
    def _refresh_window_position(self) -> bool:
        """
        Refresh window position before taking screenshot.
        
        This ensures we always capture the correct area even if:
        - User moved the window
        - User resized the window
        - Window was minimized/restored
        
        Returns:
            bool: True if window found and position updated
        """
        try:
            import win32gui
            import win32con
            
            # Check if window still exists
            if not self.hwnd or not win32gui.IsWindow(self.hwnd):
                logger.warning("  ⚠ Window handle invalid, searching for window again...")
                result = WindowManager.find_comet_window(keywords=["New Tab - Comet", "Comet"])
                if not result:
                    logger.error("  ✗ Could not find Comet window")
                    return False
                self.hwnd, self.window_rect = result
                logger.info(f"  ✓ Window re-acquired: {self.window_rect}")
                return True
            
            # Get current window position
            new_rect = win32gui.GetWindowRect(self.hwnd)
            
            # Check if position changed
            if new_rect != self.window_rect:
                old_rect = self.window_rect
                self.window_rect = new_rect
                logger.info(f"  ↻ Window position updated: {old_rect} → {new_rect}")
            
            # Check if window is minimized
            if win32gui.IsIconic(self.hwnd):
                logger.warning("  ⚠ Window is minimized, restoring...")
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)
                self.window_rect = win32gui.GetWindowRect(self.hwnd)
                logger.info(f"  ✓ Window restored: {self.window_rect}")
            
            return True
            
        except Exception as e:
            logger.error(f"  ✗ Failed to refresh window position: {e}")
            return False
    
    def _step_8_detect_stop_logo(self) -> StepResult:
        """Step 8: Periodically detect stop logo to determine task completion"""
        logger.info("")
        logger.info("[STEP 8/9] Monitoring for stop logo...")
        
        try:
            max_attempts = 150  # 150 attempts * 2 seconds = 5 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                logger.info(f"  → Detection attempt {attempt}/{max_attempts}...")
                
                # Refresh window position EVERY iteration (critical for long monitoring)
                if not self._refresh_window_position():
                    logger.warning("  ⚠ Window position refresh failed, retrying...")
                    time.sleep(2)
                    continue
                
                # Take screenshot with current position
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = self.screenshot_dir / f"stop_detection_{timestamp}.png"
                
                screenshot = ScreenshotCapture.capture_window(self.window_rect, str(screenshot_path))
                
                # Template matching
                template_path = self.template_dir / self.TEMPLATES['stop_logo']
                
                # Check if template exists
                if not template_path.exists():
                    logger.warning(f"  ⚠ Stop logo template not found: {template_path}")
                    logger.warning(f"  ⚠ Skipping stop detection")
                    step_result = StepResult("detect_stop_logo", True,
                                           data={'method': 'skipped', 'reason': 'template_not_found'})
                    self.step_results.append(step_result)
                    return step_result
                
                threshold = self.THRESHOLDS['stop_logo']
                
                coordinates = PatternMatcher.find_pattern(
                    str(screenshot_path),
                    str(template_path),
                    self.window_rect,
                    threshold
                )
                
                if coordinates:
                    logger.info(f"  ✓ Stop logo detected at: {coordinates}")
                    logger.info(f"  ✓ Task completion detected after {attempt} attempts")
                    step_result = StepResult("detect_stop_logo", True,
                                           data={'coordinates': coordinates, 'attempts': attempt})
                    self.step_results.append(step_result)
                    return step_result
                
                # Wait 2 seconds before next attempt
                time.sleep(2)
            
            # Max attempts reached without detection
            logger.warning(f"  ⚠ Stop logo not detected after {max_attempts} attempts")
            logger.warning(f"  ⚠ Proceeding to completion anyway")
            step_result = StepResult("detect_stop_logo", True,
                                   data={'method': 'timeout', 'attempts': max_attempts})
            self.step_results.append(step_result)
            return step_result
            
        except Exception as e:
            error = f"Stop logo detection error: {e}"
            logger.error(f"  ✗ {error}")
            step_result = StepResult("detect_stop_logo", False, error=error)
            self.step_results.append(step_result)
            return step_result
    
    def _step_9_handle_completion(self) -> StepResult:
        """Step 9: Handle task completion"""
        logger.info("")
        logger.info("[STEP 9/9] Handling task completion...")
        
        try:
            # Placeholder for completion actions
            # Future: Could include actions like:
            # - Taking final screenshot
            # - Extracting results from UI
            # - Sending notifications
            # - Cleanup operations
            
            logger.info("  → Executing completion handler...")
            
            # For now, just log completion
            logger.info("  ✓ Task completion handler executed")
            
            step_result = StepResult("handle_completion", True,
                                   data={'completion_time': datetime.now().isoformat()})
            self.step_results.append(step_result)
            return step_result
            
        except Exception as e:
            error = f"Completion handler error: {e}"
            logger.error(f"  ✗ {error}")
            step_result = StepResult("handle_completion", False, error=error)
            self.step_results.append(step_result)
            return step_result
    
    # ========================================================================
    # PROGRESS TRACKING (STANDARDIZED)
    # ========================================================================
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get standardized progress information for AI task.
        
        AI tasks have 9 discrete automation steps.
        """
        total_steps = 9
        completed_steps = len([r for r in self.step_results if r.success])
        current_step = len(self.step_results) if len(self.step_results) < 9 else 9
        progress_percent = int((completed_steps / total_steps) * 100)
        
        # Get human-readable status text
        status_text = "Initializing..."
        if current_step > 0 and current_step <= len(self.step_results):
            last_step = self.step_results[-1]
            step_names = {
                'wait_initialization': 'Waiting for browser',
                'activate_window': 'Activating window',
                'find_assistant': 'Finding Assistant button',
                'click_assistant': 'Clicking Assistant',
                'find_input_box': 'Finding input box',
                'input_text': 'Typing prompt',
                'send_instruction': 'Sending instruction',
                'detect_stop_logo': 'Monitoring for completion',
                'handle_completion': 'Finalizing'
            }
            status_text = step_names.get(last_step.step_name, last_step.step_name)
        
        return {
            'has_steps': True,
            'current_step': current_step,
            'total_steps': total_steps,
            'progress_percent': progress_percent,
            'status_text': status_text,
            'details': {
                'instruction': self.instruction[:50] + '...' if len(self.instruction) > 50 else self.instruction,
                'step_results': [r.to_dict() for r in self.step_results],
                'task_type': 'ai'
            }
        }
    
    def get_automation_progress(self) -> Dict[str, Any]:
        """
        DEPRECATED: Use get_progress() instead.
        
        Kept for backward compatibility.
        """
        progress = self.get_progress()
        return {
            'total_steps': progress['total_steps'],
            'current_step': progress['current_step'],
            'completed_steps': len([r for r in self.step_results if r.success]),
            'progress_percent': progress['progress_percent'],
            'step_details': progress['details']['step_results']
        }
    
    # ========================================================================
    # COMPLETION DETECTION
    # ========================================================================
    
    def check_completion(self) -> bool:
        """
        Check if AI task has completed.
        
        For AI tasks, completion means automation sequence finished,
        not just process exit (browser detaches immediately).
        
        Returns:
            True if automation sequence completed
        """
        # AI tasks complete when automation finishes, not when process exits
        return self.automation_completed
    
    # ========================================================================
    # SERIALIZATION
    # ========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to dictionary"""
        data = super().to_dict()
        data['instruction'] = self.instruction
        data['automation_progress'] = self.get_automation_progress()
        return data


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_and_execute_ai_task(instruction: str, comet_path: str) -> AITask:
    """
    Convenience function to create and execute AI task.
    
    Args:
        instruction: The AI instruction
        comet_path: Path to Comet browser
        
    Returns:
        AITask: The created and started task
    """
    task = AITask(instruction)
    pid = task.execute(comet_path=comet_path)
    task.start(pid)
    return task

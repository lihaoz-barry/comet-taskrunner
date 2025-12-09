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

# Import overlay modules
try:
    from overlay import StatusOverlay, OverlayConfig
    OVERLAY_AVAILABLE = True
except ImportError:
    OVERLAY_AVAILABLE = False
    logging.warning("Overlay module not available")

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
    
    7-Step Automation Sequence:
    1. Launch Comet browser
    2. Activate window (force focus)
    3. Find Assistant button (template matching)
    4. Click Assistant button
    5. Find input box (template matching)
    6. Input prompt text
    7. Send instruction (Enter key)
    """
    
    # Template files (just filenames, path is in template_dir)
    TEMPLATES = {
        'assistant_button': 'comet_Assistant_Unactive.png',
        'input_box': 'comet_input_box.png',  # User needs to create this
    }
    
    # Matching thresholds
    THRESHOLDS = {
        'assistant_button': 0.3,  # Fuzzy matching
        'input_box': 0.5,  # More strict
    }
    
    # Step descriptions for overlay
    STEP_DESCRIPTIONS = {
        1: ("等待浏览器初始化", "激活窗口"),
        2: ("激活Comet窗口", "查找Assistant按钮"),
        3: ("查找Assistant按钮", "点击Assistant按钮"),
        4: ("点击Assistant按钮", "查找输入框"),
        5: ("查找输入框", "输入指令文字"),
        6: ("输入指令文字", "发送指令"),
        7: ("发送指令", "完成"),
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
        
        # Overlay system
        self.overlay = None
        if OVERLAY_AVAILABLE:
            try:
                self.overlay = StatusOverlay()
                self.overlay.set_cancel_callback(self._cancel_task)
                logger.info("✓ Overlay system initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize overlay: {e}")
                self.overlay = None
        
        logger.info(f"AITask created with instruction: {instruction[:50]}...")
        logger.info(f"Template directory: {self.template_dir}")
        logger.info(f"Screenshot directory: {self.screenshot_dir}")
        
        # Verify template directory exists
        if not self.template_dir.exists():
            logger.error(f"Template directory not found: {self.template_dir}")
            logger.error("Please ensure templates folder is in the correct location")
        else:
            logger.info(f"✓ Template directory verified: {self.template_dir}")
    
    def _cancel_task(self):
        """Cancel current automation task (ESC pressed)"""
        logger.warning("Task cancellation requested by user (ESC pressed)")
        self.automation_completed = True
        self.fail("User cancelled task")
        if self.overlay:
            self.overlay.close()
    
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
        MAIN AUTOMATION SEQUENCE - 7 Steps
        
        Runs in background thread.
        """
        logger.info("="*60)
        logger.info("STARTING AUTOMATION SEQUENCE")
        logger.info(f"Task ID: {self.task_id}")
        logger.info(f"Instruction: {self.instruction}")
        logger.info("="*60)
        
        # Show overlay at start
        if self.overlay:
            try:
                self.overlay.show()
                self._update_overlay_step(0)
            except Exception as e:
                logger.warning(f"Failed to show overlay: {e}")
        
        try:
            # Step 1: Wait for browser initialization
            self._update_overlay_step(1)
            self._step_1_wait_for_initialization()
            
            # Step 2: Activate window
            self._update_overlay_step(2)
            result = self._step_2_activate_window()
            if not result.success:
                self.fail(f"Step 2 failed: {result.error}")
                return
            
            # Step 3: Find Assistant button
            self._update_overlay_step(3)
            result = self._step_3_find_assistant()
            if not result.success:
                self.fail(f"Step 3 failed: {result.error}")
                return
            assistant_coords = result.data['coordinates']
            
            # Step 4: Click Assistant button
            self._update_overlay_step(4)
            result = self._step_4_click_assistant(assistant_coords)
            if not result.success:
                self.fail(f"Step 4 failed: {result.error}")
                return
            
            # Step 5: Find input box
            self._update_overlay_step(5)
            result = self._step_5_find_input_box()
            if not result.success:
                self.fail(f"Step 5 failed: {result.error}")
                return
            input_coords = result.data['coordinates']
            
            # Step 6: Input text
            self._update_overlay_step(6)
            result = self._step_6_input_text(input_coords)
            if not result.success:
                self.fail(f"Step 6 failed: {result.error}")
                return
            
            # Step 7: Send instruction
            self._update_overlay_step(7)
            result = self._step_7_send()
            if not result.success:
                self.fail(f"Step 7 failed: {result.error}")
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
        
        finally:
            # Hide overlay when done
            if self.overlay:
                try:
                    time.sleep(1)  # Brief pause to show completion
                    self.overlay.close()
                except Exception as e:
                    logger.warning(f"Failed to close overlay: {e}")
    
    # ========================================================================
    # OVERLAY INTEGRATION
    # ========================================================================
    
    def _update_overlay_step(self, step_number: int):
        """
        Update overlay with current step information.
        
        Args:
            step_number: Current step number (0-7)
        """
        if not self.overlay:
            return
        
        try:
            # Get step descriptions
            if step_number in self.STEP_DESCRIPTIONS:
                current_desc, next_desc = self.STEP_DESCRIPTIONS[step_number]
            else:
                current_desc = "准备开始..."
                next_desc = "等待浏览器初始化"
            
            # Update overlay
            self.overlay.update_status(
                current_step=step_number,
                total_steps=7,
                step_description=current_desc,
                next_step_description=next_desc
            )
        except Exception as e:
            logger.warning(f"Failed to update overlay: {e}")
    
    # ========================================================================
    # AUTOMATION STEPS
    # ========================================================================
    
    def _step_1_wait_for_initialization(self):
        """Step 1: Wait for browser to initialize"""
        logger.info("")
        logger.info("[STEP 1/7] Waiting for browser initialization...")
        
        time.sleep(8)  # Give Comet more time to start (increased from 5s)
        
        result = StepResult("wait_initialization", True, 
                          data={'wait_time': 8})
        self.step_results.append(result)
        
        logger.info("  ✓ Browser initialization wait completed")
    
    def _step_2_activate_window(self) -> StepResult:
        """Step 2: Find and activate Comet window"""
        logger.info("")
        logger.info("[STEP 2/7] Activating Comet window...")
        
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
        logger.info("[STEP 3/7] Finding Assistant button...")
        
        try:
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
        logger.info("[STEP 4/7] Clicking Assistant button...")
        
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
        logger.info("[STEP 5/7] Finding input box...")
        
        try:
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
        logger.info("[STEP 6/7] Inputting prompt text...")
        
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
        logger.info("[STEP 7/7] Sending instruction...")
        
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
    
    # ========================================================================
    # PROGRESS TRACKING
    # ========================================================================
    
    def get_automation_progress(self) -> Dict[str, Any]:
        """
        Get automation progress information.
        
        Returns:
            Dict with progress details
        """
        total_steps = 7
        completed_steps = len([r for r in self.step_results if r.success])
        current_step = len(self.step_results) if len(self.step_results) < 7 else 7
        
        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'current_step': current_step,
            'progress_percent': int((completed_steps / total_steps) * 100),
            'step_details': [r.to_dict() for r in self.step_results]
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

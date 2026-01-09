import time
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from . import BaseAction, StepResult
from automation import ScreenshotCapture, PatternMatcher, WindowManager

logger = logging.getLogger(__name__)

class DetectLoopAction(BaseAction):
    """
    Action to monitor the screen for a condition over time (loop).
    
    Inputs (Config):
        template (str): Template filename to look for
        mode (str): 'wait_until_disappears' or 'wait_until_appears' (default: disappears)
        threshold (float): Detection threshold (default 0.8)
        timeout (float): Max time to loop in seconds (default 300.0)
        check_interval (float): Delay between checks in seconds (default 2.0)
        on_timeout (str): 'fail' or 'continue' (default: fail)
        
    Outputs (StepResult.data):
        status (str): Final status ('disappeared', 'appeared', 'timeout')
        attempts (int): Number of checks performed
        
    Effect:
        Repeatedly takes screenshots and checks for the template until condition met or timeout.
        Updates window position dynamically during the loop.
    """
    
    @property
    def action_type(self) -> str:
        return "detect_loop"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute monitoring loop"""
        template_name = config.get('template')
        threshold = float(config.get('threshold', 0.8))
        timeout = float(config.get('timeout', 300.0))
        check_interval = float(config.get('check_interval', 2.0))
        mode = config.get('mode', 'wait_until_disappears')
        
        if not template_name:
            return StepResult(self.action_type, False, error="Template name required")
            
        template_dir = context.get('template_dir')
        template_path = template_dir / template_name
        
        # If template doesn't exist, we can't match. 
        # AITask logic says: if not found, skip.
        if not template_path.exists():
            return StepResult(self.action_type, True, data={'reason': 'template_not_found', 'skipped': True})
            
        screenshot_dir = Path("screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        
        start_time = time.time()
        attempt = 0
        
        while (time.time() - start_time) < timeout:
            attempt += 1
            try:
                # 1. Refresh window position (AITask logic)
                hwnd_info = WindowManager.find_comet_window(keywords=["New Tab - Comet", "Comet", "New Tab"])
                if not hwnd_info:
                    time.sleep(check_interval)
                    continue
                    
                hwnd, window_rect = hwnd_info
                
                # 2. Capture screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Overwrite/reuse file to save space? Or keep history?
                # AITask kept history. Let's keep it but minimal.
                screenshot_path = screenshot_dir / f"monitor_{template_name}_{timestamp}.png"
                
                ScreenshotCapture.capture_window(window_rect, str(screenshot_path))
                
                # 3. Match
                debug_mode = True # Always debug for now per user request
                result = PatternMatcher.find_pattern(
                    str(screenshot_path),
                    str(template_path),
                    window_rect,
                    threshold,
                    save_debug=debug_mode
                )
                
                # 4. Check condition
                if mode == 'wait_until_disappears':
                    if not result:
                         # Disappeared!
                        return StepResult(self.action_type, True, data={'attempts': attempt, 'status': 'disappeared'})
                    else:
                        # Unpack result for logging
                        center_coords, match_box, confidence = result
                        logger.debug(f"Template still visible at {center_coords} (confidence: {confidence:.4f})")
                        
                elif mode == 'wait_until_appears':
                    if result:
                        # Appeared!
                        center_coords, match_box, confidence = result
                        return StepResult(self.action_type, True, data={
                            'attempts': attempt,
                            'coordinates': center_coords,
                            'match_box': match_box,
                            'confidence': confidence
                        })
                
                # Clean up screenshot
                # os.remove(screenshot_path)
                
            except Exception as e:
                logger.warning(f"Monitor error: {e}")
                
            time.sleep(check_interval)
            
        # Timeout
        on_timeout = config.get('on_timeout', 'fail')
        if on_timeout == 'continue':
             return StepResult(self.action_type, True, data={'reason': 'timeout', 'attempts': attempt})
        else:
             return StepResult(self.action_type, False, error=f"Timeout waiting for condition: {mode}")

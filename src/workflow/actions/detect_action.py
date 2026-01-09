import time
import logging
import tempfile
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from . import BaseAction, StepResult
# Import automation components
from automation import ScreenshotCapture, PatternMatcher, WindowManager

logger = logging.getLogger(__name__)

class DetectAction(BaseAction):
    """
    Action to find visual elements on screen using template matching.
    
    Inputs (Config):
        template (str): Filename of the template image (must exist in template_dir)
        threshold (float): Matching confidence threshold 0.0-1.0 (default 0.8)
        timeout (float): Max time to search in seconds (default 10.0)
        retry_interval (float): Delay between checks (default 0.5)
        
    Outputs (StepResult.data):
        coordinates (tuple): (x, y) center coordinates of match
        window_rect (tuple): Current window bounds
        hwnd (int): Window handle ID
        
    Effect:
        Captures screenshots of the target window.
        Performs OpenCV template matching.
        Returns coordinates if found, fails if timeout reached.
    """
    
    @property
    def action_type(self) -> str:
        return "detect"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """
        Execute detection.
        
        Args:
            config: Configuration dictionary
            context: Workflow context (must contain 'template_dir')
        """
        template_name = config.get('template')
        threshold = float(config.get('threshold', 0.8))
        timeout = float(config.get('timeout', 10.0))
        retry_interval = float(config.get('retry_interval', 0.5))
        
        if not template_name:
            return StepResult(self.action_type, False, error="Template name required")
            
        template_dir = context.get('template_dir')
        if not template_dir:
            return StepResult(self.action_type, False, error="Template directory not found in context")
            
        template_path = template_dir / template_name
        if not template_path.exists():
            return StepResult(self.action_type, False, error=f"Template file not found: {template_path}")
            
        # Get screenshot directory (use temp directory to avoid permission issues in exe)
        # Using system temp directory to ensure write access
        screenshot_dir = Path(tempfile.gettempdir()) / "comet_taskrunner" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                # 1. Get window rect (assume active window or find fresh)
                # Ideally we track the active HWND in context from WindowAction?
                # But windows move. Let's find Comet window again or use cached if reliable?
                # AITask refreshes it every time.
                # Let's try to find generic "Comet" or "New Tab" window
                # TODO: Optimize this by caching HWND in context and verifying it
                
                hwnd_info = WindowManager.find_comet_window(keywords=["New Tab - Comet", "Comet", "New Tab"])
                if not hwnd_info:
                     # Wait and retry
                    time.sleep(retry_interval)
                    continue
                    
                hwnd, window_rect = hwnd_info
                
                # 2. Capture screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = screenshot_dir / f"detect_{template_name}_{timestamp}.png"
                
                ScreenshotCapture.capture_window(window_rect, str(screenshot_path))
                
                # 3. Match
                debug_mode = config.get('debug', True) # Default to True for now as per user request
                
                result = PatternMatcher.find_pattern(
                    str(screenshot_path),
                    str(template_path),
                    window_rect,
                    threshold,
                    save_debug=debug_mode
                )
                
                if result:
                    # Unpack new return format: (center_coords, match_box, confidence)
                    center_coords, match_box, confidence = result
                    
                    # Calculate click position based on configuration
                    from automation.click_position import ClickPosition
                    
                    click_pos_config = config.get('click_position', 'center')
                    
                    try:
                        click_coords = ClickPosition.calculate(
                            match_box=match_box,
                            window_rect=window_rect,
                            position_config=click_pos_config
                        )
                        
                        logger.info(f"Click position calculated: {click_coords} "
                                   f"(config: {click_pos_config}, confidence: {confidence:.4f})")
                        
                    except Exception as e:
                        logger.warning(f"Failed to calculate click position: {e}, using center")
                        click_coords = center_coords
                    
                    return StepResult(self.action_type, True, data={
                        'coordinates': click_coords,  # 点击坐标 (可能调整过)
                        'center': center_coords,      # 原始中心点
                        'match_box': match_box,       # 匹配框 (x, y, w, h)
                        'confidence': confidence,     # 匹配度
                        'click_position_config': click_pos_config,  # 使用的配置
                        'window_rect': window_rect,
                        'hwnd': hwnd
                    })
                    
                # Clean up screenshot if not useful (optional)
                # os.remove(screenshot_path) 
                
            except Exception as e:
                logger.warning(f"Detection error: {e}")
                
            time.sleep(retry_interval)
            
        return StepResult(self.action_type, False, error=f"Template {template_name} not found after {timeout}s")

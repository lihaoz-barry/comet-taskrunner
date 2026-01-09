import logging
import base64
import tempfile
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from . import BaseAction, StepResult

logger = logging.getLogger(__name__)


class ScreenshotAction(BaseAction):
    """
    Action to capture screenshots.
    
    Inputs (Config):
        region (str): 'full_window' | 'coordinates' (default: full_window)
        coordinates (dict): {x, y, width, height} - only if region='coordinates'
        save_path (str): Path to save screenshot (supports {timestamp} placeholder)
        encode_base64 (bool): Whether to include base64 encoded image (default: False)
        
    Outputs (StepResult.data):
        image_path (str): Absolute path to saved screenshot
        image_base64 (str): Base64 encoded image (if encode_base64=True)
        region (tuple): The captured region coordinates
        
    Effect:
        Captures screen region and optionally saves to file.
    """
    
    @property
    def action_type(self) -> str:
        return "screenshot"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute screenshot capture"""
        from automation import ScreenshotCapture, WindowManager
        
        region_type = config.get('region', 'full_window')
        save_path = config.get('save_path')
        encode_base64 = config.get('encode_base64', False)
        
        try:
            # Determine capture region
            if region_type == 'full_window':
                # Get current active window rect from context or find it
                result = WindowManager.find_comet_window()
                if not result:
                    return StepResult(self.action_type, False, error="No window found for screenshot")
                _, rect = result
            elif region_type == 'coordinates':
                coords = config.get('coordinates', {})
                x = int(coords.get('x', 0))
                y = int(coords.get('y', 0))
                width = int(coords.get('width', 800))
                height = int(coords.get('height', 600))
                rect = (x, y, x + width, y + height)
            else:
                return StepResult(self.action_type, False, error=f"Unknown region type: {region_type}")
            
            # Process save path
            if save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = save_path.replace('{timestamp}', timestamp)
                # Make absolute if relative
                save_path = str(Path(save_path).resolve())
            else:
                # Default save location
                import sys
                if getattr(sys, 'frozen', False):
                    # Use temp directory for exe to avoid permission issues
                    base_dir = Path(tempfile.gettempdir()) / "comet_taskrunner"
                else:
                    base_dir = Path(__file__).parent.parent.parent.parent
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshots_dir = base_dir / "screenshots"
                screenshots_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
                save_path = str(screenshots_dir / f"capture_{timestamp}.png")
            
            # Capture screenshot
            screenshot = ScreenshotCapture.capture_window(rect, save_path)
            
            output_data = {
                'image_path': save_path,
                'region': rect
            }
            
            # Optional base64 encoding
            if encode_base64:
                import io
                buffer = io.BytesIO()
                screenshot.save(buffer, format='PNG')
                buffer.seek(0)
                output_data['image_base64'] = base64.b64encode(buffer.read()).decode('utf-8')
            
            logger.info(f"Screenshot captured: {save_path}")
            return StepResult(self.action_type, True, data=output_data)
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            import traceback
            traceback.print_exc()
            return StepResult(self.action_type, False, error=str(e))

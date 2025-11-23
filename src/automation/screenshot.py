"""
Automation Module - Screenshot Capture

MSS-based screenshot capture with multi-monitor support.
Extracted from OpenCV-sample demo_image_ui.py
"""

import logging
from pathlib import Path
from typing import Tuple
from mss import mss
from PIL import Image

logger = logging.getLogger(__name__)


class ScreenshotCapture:
    """
    Multi-monitor screenshot capture using MSS.
    
    Features:
    - Supports negative coordinates (secondary monitors)
    - Faster than PyAutoGUI
    - Direct pixel access
    """
    
    @staticmethod
    def capture_window(rect: Tuple[int, int, int, int], save_path: str = None) -> Image.Image:
        """
        Capture a window region.
        
        Args:
            rect: Window rectangle (left, top, right, bottom)
            save_path: Optional path to save screenshot
            
        Returns:
            PIL Image object
        """
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        
        logger.info(f"Capturing region ({left}, {top}, {width}, {height})")
        
        try:
            with mss() as sct:
                monitor = {
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height
                }
                
                sct_img = sct.grab(monitor)
                screenshot = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                logger.info(f"Captured {screenshot.size[0]}x{screenshot.size[1]} pixels")
                
                if save_path:
                    ScreenshotCapture.save_screenshot(screenshot, save_path)
                
                return screenshot
                
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            raise
    
    @staticmethod
    def save_screenshot(image: Image.Image, filepath: str) -> None:
        """
        Save screenshot to file.
        
        Args:
            image: PIL Image
            filepath: Destination path
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            image.save(
                filepath,
                format='PNG',
                compress_level=1,
                optimize=False
            )
            
            file_size = Path(filepath).stat().st_size / 1024
            logger.info(f"Screenshot saved: {filepath} ({file_size:.1f} KB)")
            
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            raise

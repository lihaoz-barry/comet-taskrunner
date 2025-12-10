"""
Automation Module - Pattern Matching

OpenCV-based template matching with fuzzy matching support.
Extracted from OpenCV-sample demo_image_ui.py
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class PatternMatcher:
    """
    OpenCV template matching for UI automation.
    
    Features:
    - Fuzzy matching (configurable threshold)
    - Multiple retry support
    - Screen coordinate conversion
    """
    
    @staticmethod
    def find_pattern(
        screenshot_path: str,
        template_path: str,
        window_rect: Tuple[int, int, int, int],
        threshold: float = 0.3,
        save_debug: bool = False
    ) -> Optional[Tuple[int, int]]:
        """
        Find template pattern in screenshot.
        
        Args:
            screenshot_path: Path to screenshot image
            template_path: Path to template image
            window_rect: Window coordinates (left, top, right, bottom)
            threshold: Matching confidence threshold (0.0-1.0)
            save_debug: If True, save a debug image with the match highlighted
            
        Returns:
            (x, y) screen coordinates of pattern center, or None
        """
        logger.info(f"Starting pattern matching: template={Path(template_path).name}, threshold={threshold}")
        
        try:
            # Load images
            screenshot = cv2.imread(str(screenshot_path))
            template = cv2.imread(str(template_path))
            
            if screenshot is None:
                logger.error(f"Failed to load screenshot: {screenshot_path}")
                return None
            
            if template is None:
                logger.error(f"Failed to load template: {template_path}")
                return None
            
            screenshot_h, screenshot_w = screenshot.shape[:2]
            template_h, template_w = template.shape[:2]
            
            logger.debug(f"Screenshot: {screenshot_w}x{screenshot_h}, Template: {template_w}x{template_h}")
            
            # Perform matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            logger.info(f"Best match confidence: {max_val:.4f}")
            
            if max_val < threshold:
                logger.warning(f"No match found (confidence {max_val:.4f} < threshold {threshold})")
                return None
            
            # Calculate screen coordinates
            left, top, right, bottom = window_rect
            match_x, match_y = max_loc
            center_x = left + match_x + template_w // 2
            center_y = top + match_y + template_h // 2
            
            logger.info(f"Pattern found! Confidence={max_val:.4f}, "
                       f"Position in screenshot=({match_x}, {match_y}), "
                       f"Screen coordinates=({center_x}, {center_y})")
            
            # Save debug image if requested
            if save_debug:
                try:
                    debug_img = screenshot.copy()
                    # Draw Red Rectangle (BGR)
                    cv2.rectangle(
                        debug_img, 
                        (match_x, match_y), 
                        (match_x + template_w, match_y + template_h), 
                        (0, 0, 255), 
                        2
                    )
                    # Add text
                    cv2.putText(
                        debug_img, 
                        f"Conf: {max_val:.2f}", 
                        (match_x, match_y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, 
                        (0, 0, 255), 
                        1
                    )
                    
                    debug_path = Path(screenshot_path).parent / f"debug_match_{Path(template_path).stem}.png"
                    cv2.imwrite(str(debug_path), debug_img)
                    logger.info(f"Saved visual debug image: {debug_path}")
                except Exception as e:
                    logger.warning(f"Failed to save debug image: {e}")
            
            return (center_x, center_y)
            
        except Exception as e:
            logger.error(f"Pattern matching failed: {e}")
            return None
    
    @staticmethod
    def find_pattern_with_retry(
        screenshot_path: str,
        template_path: str,
        window_rect: Tuple[int, int, int, int],
        threshold: float = 0.3,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Optional[Tuple[int, int]]:
        """
        Find pattern with retry logic.
        
        Args:
            screenshot_path: Path to screenshot
            template_path: Path to template
            window_rect: Window rectangle
            threshold: Matching threshold
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
            
        Returns:
            (x, y) coordinates or None
        """
        import time
        
        for attempt in range(max_retries):
            logger.info(f"Pattern matching attempt {attempt + 1}/{max_retries}")
            
            result = PatternMatcher.find_pattern(
                screenshot_path, template_path, window_rect, threshold
            )
            
            if result:
                return result
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        
        logger.error(f"Pattern not found after {max_retries} attempts")
        return None

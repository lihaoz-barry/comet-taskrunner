"""
Automation Module - Mouse & Keyboard Control

PyAutoGUI-based input automation.
Extracted from OpenCV-sample demo_image_ui.py
"""

import pyautogui
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class MouseController:
    """
    Mouse and keyboard automation controller.
    
    Features:
    - Mouse movement with animation
    - Click operations
    - Keyboard input
    - Key press simulation
    """
    
    @staticmethod
    def move_to(x: int, y: int, duration: float = 0.5) -> None:
        """
        Move mouse to coordinates with animation.
        
        Args:
            x: Screen X coordinate
            y: Screen Y coordinate
            duration: Animation duration in seconds
        """
        logger.info(f"Moving mouse to ({x}, {y}) with {duration}s animation")
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.debug("Mouse movement completed")
        except Exception as e:
            logger.error(f"Mouse movement failed: {e}")
            raise
    
    @staticmethod
    def click(x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1, interval: float = 0.0) -> None:
        """
        Click at coordinates or current position.
        
        Args:
            x: Optional X coordinate (None = current position)
            y: Optional Y coordinate
            clicks: Number of clicks (1=single, 2=double)
            interval: Delay between clicks
        """
        if x is not None and y is not None:
            logger.info(f"Clicking at ({x}, {y}), clicks={clicks}")
            try:
                pyautogui.click(x, y, clicks=clicks, interval=interval)
                logger.debug("Click completed")
            except Exception as e:
                logger.error(f"Click failed: {e}")
                raise
        else:
            logger.info(f"Clicking at current position, clicks={clicks}")
            try:
                pyautogui.click(clicks=clicks, interval=interval)
                logger.debug("Click completed")
            except Exception as e:
                logger.error(f"Click failed: {e}")
                raise
    
    @staticmethod
    def type_text(text: str, interval: float = 0.05) -> None:
        """
        Type text with keyboard.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes
        """
        logger.info(f"Typing text (length={len(text)}, interval={interval}s)")
        logger.debug(f"Text preview: {text[:50]}...")
        
        try:
            pyautogui.write(text, interval=interval)
            logger.debug("Text input completed")
        except Exception as e:
            logger.error(f"Text input failed: {e}")
            raise
    
    @staticmethod
    def press_key(key: str, presses: int = 1, interval: float = 0.0) -> None:
        """
        Press a key.
        
        Args:
            key: Key name (e.g., 'enter', 'tab', 'ctrl')
            presses: Number of times to press
            interval: Delay between presses
        """
        logger.info(f"Pressing key '{key}' {presses} time(s)")
        
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            logger.debug(f"Key press completed")
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            raise
    
    @staticmethod
    def hotkey(*keys) -> None:
        """
        Press key combination (e.g., Ctrl+C).
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
        """
        keys_str = '+'.join(keys)
        logger.info(f"Pressing hotkey: {keys_str}")
        
        try:
            pyautogui.hotkey(*keys)
            logger.debug("Hotkey completed")
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
            raise

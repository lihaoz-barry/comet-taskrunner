"""
Automation Module

Provides window management, screenshot capture, pattern matching,
and mouse/keyboard control for UI automation.
"""

from .window_manager import WindowManager
from .screenshot import ScreenshotCapture
from .pattern_matcher import PatternMatcher
from .mouse_controller import MouseController
from .click_position import ClickPosition

__all__ = [
    'WindowManager',
    'ScreenshotCapture',
    'PatternMatcher',
    'MouseController',
    'ClickPosition'
]

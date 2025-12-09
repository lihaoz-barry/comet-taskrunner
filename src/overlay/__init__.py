"""
Overlay Module

Provides desktop status overlay system for automation tasks.
"""

from .status_overlay import StatusOverlay
from .overlay_config import OverlayConfig, OverlayPosition
from .system_tray import SystemTray
from .keyboard_handler import KeyboardHandler

__all__ = [
    'StatusOverlay',
    'OverlayConfig',
    'OverlayPosition',
    'SystemTray',
    'KeyboardHandler'
]

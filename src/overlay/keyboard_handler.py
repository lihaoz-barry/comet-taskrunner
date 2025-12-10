"""
Keyboard Handler

Monitors ESC key for task cancellation.
"""

import logging
import threading

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    logging.warning("keyboard module not available - ESC key cancellation disabled")

logger = logging.getLogger(__name__)


class KeyboardHandler:
    """Keyboard event handler for task cancellation"""
    
    def __init__(self):
        """Initialize keyboard handler"""
        self.cancel_callback = None
        self.listening = False
        self._hook = None
        
        if not KEYBOARD_AVAILABLE:
            logger.warning("Keyboard handler disabled (keyboard module not available)")
    
    def start_listening(self, cancel_callback):
        """
        Start listening for ESC key.
        
        Args:
            cancel_callback: Function to call when ESC is pressed
        """
        if not KEYBOARD_AVAILABLE:
            logger.debug("Keyboard listening not available")
            return
        
        if self.listening:
            return
        
        self.cancel_callback = cancel_callback
        self.listening = True
        
        try:
            # Register ESC key handler
            keyboard.on_press_key('esc', self._on_esc_pressed, suppress=False)
            logger.info("ESC key listener started")
        except Exception as e:
            logger.warning(f"Failed to start keyboard listener: {e}")
            logger.warning("ESC key cancellation will not be available")
            self.listening = False
    
    def stop_listening(self):
        """Stop listening for ESC key"""
        if not KEYBOARD_AVAILABLE:
            return
        
        if not self.listening:
            return
        
        try:
            keyboard.unhook_all()
            self.listening = False
            logger.info("ESC key listener stopped")
        except Exception as e:
            logger.warning(f"Failed to stop keyboard listener: {e}")
    
    def _on_esc_pressed(self, event):
        """Handle ESC key press"""
        if self.cancel_callback:
            logger.info("ESC key pressed - triggering cancellation")
            try:
                self.cancel_callback()
            except Exception as e:
                logger.error(f"Error in cancel callback: {e}")

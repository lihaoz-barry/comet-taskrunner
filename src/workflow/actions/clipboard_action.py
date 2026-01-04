import logging
from typing import Dict, Any
from . import BaseAction, StepResult

logger = logging.getLogger(__name__)

# Use pyperclip for cross-platform clipboard access
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False
    logger.warning("pyperclip not available, trying win32clipboard")

# Fallback to win32clipboard on Windows
try:
    import win32clipboard
    import win32con
    HAS_WIN32CLIPBOARD = True
except ImportError:
    HAS_WIN32CLIPBOARD = False


class ClipboardAction(BaseAction):
    """
    Action to interact with system clipboard.
    
    Inputs (Config):
        operation (str): 'copy' | 'paste' | 'get' | 'set'
            - copy: Simulates Ctrl+C to copy selected content
            - paste: Simulates Ctrl+V to paste clipboard content
            - get: Returns current clipboard text content
            - set: Sets clipboard to specified text
        text (str): Text to set (only for 'set' operation)
        
    Outputs (StepResult.data):
        content (str): The clipboard text content (for 'get' operation)
        
    Effect:
        Reads or modifies system clipboard.
    """
    
    @property
    def action_type(self) -> str:
        return "clipboard"
    
    def execute(self, config: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """Execute clipboard operation"""
        operation = config.get('operation', 'get')
        
        if operation == 'get':
            return self._get_clipboard()
        elif operation == 'set':
            text = config.get('text', '')
            # Resolve text if it's a reference
            if isinstance(text, str) and text.startswith('inputs.'):
                text = context.get('inputs', {}).get(text.split('.')[1], text)
            return self._set_clipboard(text)
        elif operation == 'copy':
            return self._simulate_copy()
        elif operation == 'paste':
            return self._simulate_paste()
        else:
            return StepResult(self.action_type, False, error=f"Unknown operation: {operation}")
    
    def _get_clipboard(self) -> StepResult:
        """Get current clipboard text content"""
        try:
            if HAS_PYPERCLIP:
                content = pyperclip.paste()
                return StepResult(self.action_type, True, data={'content': content})
            elif HAS_WIN32CLIPBOARD:
                win32clipboard.OpenClipboard()
                try:
                    content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                finally:
                    win32clipboard.CloseClipboard()
                return StepResult(self.action_type, True, data={'content': content})
            else:
                return StepResult(self.action_type, False, error="No clipboard library available")
        except Exception as e:
            logger.error(f"Failed to get clipboard: {e}")
            return StepResult(self.action_type, False, error=str(e))
    
    def _set_clipboard(self, text: str) -> StepResult:
        """Set clipboard text content"""
        try:
            if HAS_PYPERCLIP:
                pyperclip.copy(text)
                return StepResult(self.action_type, True, data={'content': text})
            elif HAS_WIN32CLIPBOARD:
                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
                finally:
                    win32clipboard.CloseClipboard()
                return StepResult(self.action_type, True, data={'content': text})
            else:
                return StepResult(self.action_type, False, error="No clipboard library available")
        except Exception as e:
            logger.error(f"Failed to set clipboard: {e}")
            return StepResult(self.action_type, False, error=str(e))
    
    def _simulate_copy(self) -> StepResult:
        """Simulate Ctrl+C keypress"""
        try:
            from automation import MouseController
            import time
            
            # Press Ctrl+C
            MouseController.hotkey('ctrl', 'c')
            time.sleep(0.3)  # Wait for clipboard to update
            
            # Get the copied content
            result = self._get_clipboard()
            if result.success:
                return StepResult(self.action_type, True, data={'content': result.data.get('content', '')})
            return result
        except Exception as e:
            logger.error(f"Failed to simulate copy: {e}")
            return StepResult(self.action_type, False, error=str(e))
    
    def _simulate_paste(self) -> StepResult:
        """Simulate Ctrl+V keypress"""
        try:
            from automation import MouseController
            
            # Press Ctrl+V
            MouseController.hotkey('ctrl', 'v')
            return StepResult(self.action_type, True, data={})
        except Exception as e:
            logger.error(f"Failed to simulate paste: {e}")
            return StepResult(self.action_type, False, error=str(e))

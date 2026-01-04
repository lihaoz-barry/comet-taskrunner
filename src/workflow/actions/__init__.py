from .base_action import BaseAction, StepResult
from ..step_executor import ActionRegistry

# Import all actions to register them
from .wait_action import WaitAction
from .window_action import WindowAction
from .detect_action import DetectAction
from .click_action import ClickAction
from .click_and_type_action import ClickAndTypeAction
from .key_press_action import KeyPressAction
from .detect_loop_action import DetectLoopAction
from .completion_action import CompletionAction
from .close_window_action import CloseWindowAction
from .clipboard_action import ClipboardAction
from .screenshot_action import ScreenshotAction
from .webhook_action import WebhookAction

# Register actions
ActionRegistry.register(WaitAction)
ActionRegistry.register(WindowAction)
ActionRegistry.register(DetectAction)
ActionRegistry.register(ClickAction)
ActionRegistry.register(ClickAndTypeAction)
ActionRegistry.register(KeyPressAction)
ActionRegistry.register(DetectLoopAction)
ActionRegistry.register(CompletionAction)
ActionRegistry.register(CloseWindowAction)
ActionRegistry.register(ClipboardAction)
ActionRegistry.register(ScreenshotAction)
ActionRegistry.register(WebhookAction)

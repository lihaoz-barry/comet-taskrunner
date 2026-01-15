"""
Bounding Box Overlay

Displays a red bounding box with gradient fade-in/out animation
to provide visual feedback when a widget is detected.
"""

import tkinter as tk
import threading
import time
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class BoundingBoxOverlay:
    """
    Transparent overlay window that displays an animated red bounding box
    at the location of detected widgets.
    
    Features:
    - Gradient fade-in/out animation
    - Always-on-top, click-through window
    - Auto-cleanup after animation
    - Thread-safe operation
    """
    
    # Animation configuration
    FADE_IN_DURATION = 0.3  # seconds
    FADE_OUT_DURATION = 0.3  # seconds
    DISPLAY_DURATION = 0.5  # seconds to display at full opacity
    FRAME_INTERVAL = 0.02  # seconds between animation frames (50 FPS)
    
    def __init__(self):
        """Initialize the bounding box overlay"""
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.running = False
        self.lock = threading.Lock()
        
        logger.info("BoundingBoxOverlay initialized")
    
    def show_bounding_box(self, x: int, y: int, width: int, height: int):
        """
        Display an animated bounding box at the specified screen coordinates.
        
        Args:
            x: Left coordinate of the bounding box
            y: Top coordinate of the bounding box
            width: Width of the bounding box
            height: Height of the bounding box
        """
        logger.info(f"Showing bounding box at ({x}, {y}) with size {width}x{height}")
        
        # Create and run the animation in a separate thread
        # Each overlay instance is independent
        animation_thread = threading.Thread(
            target=self._animate_box,
            args=(x, y, width, height),
            daemon=True
        )
        animation_thread.start()
    
    def _animate_box(self, x: int, y: int, width: int, height: int):
        """
        Animation sequence: fade in -> display -> fade out -> cleanup
        
        Args:
            x, y, width, height: Bounding box coordinates
        """
        try:
            # Create window (tkinter handles threading internally)
            self._create_window(x, y, width, height)
            
            # Fade in
            self._fade_animation(0.0, 1.0, self.FADE_IN_DURATION)
            
            # Display at full opacity
            time.sleep(self.DISPLAY_DURATION)
            
            # Fade out
            self._fade_animation(1.0, 0.0, self.FADE_OUT_DURATION)
            
            # Cleanup
            self._destroy_window()
            
        except Exception as e:
            logger.error(f"Animation error: {e}")
            self._destroy_window()
    
    def _create_window(self, x: int, y: int, width: int, height: int):
        """
        Create the transparent overlay window with red rectangle.
        
        Args:
            x, y: Screen coordinates for top-left corner
            width, height: Dimensions of the bounding box
        """
        with self.lock:
            if self.root:
                return
            
            self.root = tk.Tk()
            self.root.withdraw()  # Start hidden
            
            # Window properties
            self.root.overrideredirect(True)  # No window decorations
            self.root.attributes('-topmost', True)  # Always on top
            self.root.attributes('-alpha', 0.0)  # Start fully transparent
            
            # Hide from taskbar (Windows)
            try:
                self.root.attributes('-toolwindow', True)
            except tk.TclError:
                pass
            
            # Make click-through (Windows)
            try:
                import ctypes
                self.root.update()
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if hwnd:
                    GWL_EXSTYLE = -20
                    WS_EX_LAYERED = 0x80000
                    WS_EX_TRANSPARENT = 0x20
                    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                    ctypes.windll.user32.SetWindowLongW(
                        hwnd, GWL_EXSTYLE, 
                        style | WS_EX_LAYERED | WS_EX_TRANSPARENT
                    )
            except Exception as e:
                logger.warning(f"Failed to make window click-through: {e}")
            
            # Set window size and position
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Create canvas for drawing
            self.canvas = tk.Canvas(
                self.root,
                width=width,
                height=height,
                bg='black',
                highlightthickness=0
            )
            self.canvas.pack()
            
            # Draw red rectangle
            # Use a thick border for visibility
            border_width = 4
            self.canvas.create_rectangle(
                border_width // 2,
                border_width // 2,
                width - border_width // 2,
                height - border_width // 2,
                outline='red',
                width=border_width
            )
            
            # Show window
            self.root.deiconify()
            self.root.update()
            
            logger.debug(f"Window created at ({x}, {y}) with size {width}x{height}")
    
    def _fade_animation(self, start_alpha: float, end_alpha: float, duration: float):
        """
        Perform a gradient fade animation.
        
        Args:
            start_alpha: Starting opacity (0.0 to 1.0)
            end_alpha: Ending opacity (0.0 to 1.0)
            duration: Animation duration in seconds
        """
        if not self.root:
            return
        
        steps = int(duration / self.FRAME_INTERVAL)
        if steps <= 0:
            steps = 1
        
        alpha_delta = (end_alpha - start_alpha) / steps
        
        for i in range(steps):
            current_alpha = start_alpha + (alpha_delta * i)
            
            with self.lock:
                if self.root:
                    try:
                        self.root.attributes('-alpha', current_alpha)
                        self.root.update()
                    except tk.TclError:
                        break
            
            time.sleep(self.FRAME_INTERVAL)
        
        # Set final alpha
        with self.lock:
            if self.root:
                try:
                    self.root.attributes('-alpha', end_alpha)
                    self.root.update()
                except tk.TclError:
                    pass
    
    def _destroy_window(self):
        """Clean up and destroy the overlay window"""
        with self.lock:
            if self.root:
                try:
                    self.root.destroy()
                except Exception as e:
                    logger.warning(f"Error destroying window: {e}")
                finally:
                    self.root = None
                    self.canvas = None
                    logger.debug("Window destroyed")

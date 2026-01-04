"""
Status Overlay Window

Tkinter-based overlay that displays automation task status.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import logging
import ctypes
from typing import Optional, Dict, Any
from .overlay_config import OverlayConfig, OverlayPosition
from .keyboard_handler import KeyboardHandler

logger = logging.getLogger(__name__)


class StatusOverlay:
    """Desktop status overlay using Tkinter"""
    
    # Default automation steps count
    DEFAULT_TOTAL_STEPS = 7
    
    def __init__(self, config: OverlayConfig = None):
        """
        Initialize status overlay.
        
        Args:
            config: OverlayConfig instance (creates default if None)
        """
        self.config = config or OverlayConfig()
        
        # Window state
        self.root: Optional[tk.Tk] = None
        self.should_be_visible = False  # Target visibility state
        self.is_visible_actual = False  # Actual visibility state
        self.running = False
        
        # Status data
        self.current_step = 0
        self.total_steps = self.DEFAULT_TOTAL_STEPS
        self.step_description = "等待开始..."
        self.next_step_description = ""
        self.elapsed_time = 0
        self.start_time = 0
        
        # UI elements
        self.step_label = None
        self.current_label = None
        self.next_label = None
        self.time_label = None
        self.progress_bar = None
        
        # Thread safety
        self.lock = threading.Lock()
        self.update_pending = False
        
        # Task cancellation callback
        self.cancel_callback = None
        
        # Keyboard handler for ESC key
        self.keyboard_handler = KeyboardHandler()

    def start(self):
        """Start the overlay UI thread (persistent)"""
        if self.running:
            return
            
        self.running = True
        threading.Thread(target=self._run_overlay, daemon=True).start()
        logger.info("Overlay thread started")

    def show(self):
        """Show the overlay (thread-safe signal)"""
        self.should_be_visible = True
        
        # Restart timer if showing again
        self.start_time = time.time()
        
        # Start keyboard listener
        if self.cancel_callback:
            self.keyboard_handler.start_listening(self.cancel_callback)
        
        logger.info("Overlay show requested")
    
    def hide(self):
        """Hide the overlay (thread-safe signal)"""
        self.should_be_visible = False
        logger.info("Overlay hide requested")
    
    def close(self):
        """Close the overlay window and stop thread"""
        self.running = False
        self.should_be_visible = False
        
        # Stop keyboard listener
        self.keyboard_handler.stop_listening()
        
        # Signal main loop to quit (will be handled in _update_loop or callback)
        # We can use after to force it if needed, but the loop checks self.running
        logger.info("Overlay close requested")
    
    def update_status(self, current_step: int = None, total_steps: int = None,
                     step_description: str = None, next_step_description: str = None):
        """
        Update overlay status (thread-safe).
        """
        with self.lock:
            if current_step is not None:
                self.current_step = current_step
            if total_steps is not None:
                self.total_steps = total_steps
            if step_description is not None:
                self.step_description = step_description
            if next_step_description is not None:
                self.next_step_description = next_step_description
            
            self.update_pending = True
    
    def set_cancel_callback(self, callback):
        self.cancel_callback = callback
    
    def change_position(self, position: OverlayPosition):
        self.config.set_position(position)
        # Position update will happen in loop or next show
        # Note: changing position of existing window effectively requires main thread
        # We'll leave it for now or implement a flag
        pass

    def _create_window(self):
        """Create the Tkinter overlay window"""
        if self.root:
            return
        
        self.root = tk.Tk()
        self.root.title("TaskRunner Monitor")
        
        # Initialize hidden
        self.root.withdraw()
        
        # Window properties
        self.root.overrideredirect(True)  # No borders
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', self.config.get_opacity())  # Transparency
        
        # Windows-specific: hide from taskbar
        try:
            self.root.attributes('-toolwindow', True)
        except tk.TclError:
            pass  # Not on Windows
        
        # Get dimensions
        width, height = self.config.get_dimensions()
        self.root.geometry(f"{width}x{height}")
        
        # Windows-specific: Exclude from screen capture & Click-through
        try:
            self.root.update()  # Ensure winfo_id is valid
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd:
                WDA_EXCLUDEFROMCAPTURE = 0x00000011
                ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE) # type: ignore

                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x80000
                WS_EX_TRANSPARENT = 0x20
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE) # type: ignore
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT) # type: ignore
        except Exception as e:
            logger.warning(f"Failed to set window properties: {e}")
        
        # Set background
        bg_color = '#1a1a1a'
        self.root.configure(bg=bg_color)
        
        # Main frame with padding
        main_frame = tk.Frame(self.root, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = tk.Label(main_frame, text="🤖 AI TASK MONITOR", font=('Arial', 12, 'bold'), bg=bg_color, fg='#00ff88')
        title_label.pack(pady=(0, 2))
        
        # Separator
        tk.Frame(main_frame, bg='#444444', height=2).pack(fill=tk.X, pady=5)
        
        # Warning
        tk.Label(main_frame, text="⚡ 屏幕正在被自动控制", font=('Arial', 10, 'bold'), bg=bg_color, fg='#ffaa00').pack(pady=(5, 10))
        
        # Step info
        self.step_label = tk.Label(main_frame, text="📍 Step 0/7", font=('Arial', 10, 'bold'), bg=bg_color, fg='#ffffff')
        self.step_label.pack(anchor='w', pady=(5, 3))
        
        # Current step
        current_frame = tk.Frame(main_frame, bg=bg_color)
        current_frame.pack(fill=tk.X, pady=2)
        tk.Label(current_frame, text="正在:", font=('Arial', 9), bg=bg_color, fg='#aaaaaa').pack(side=tk.LEFT)
        self.current_label = tk.Label(current_frame, text="等待开始...", font=('Arial', 9), bg=bg_color, fg='#ffffff', wraplength=220, justify=tk.LEFT)
        self.current_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Next step
        next_frame = tk.Frame(main_frame, bg=bg_color)
        next_frame.pack(fill=tk.X, pady=2)
        tk.Label(next_frame, text="下一步:", font=('Arial', 9), bg=bg_color, fg='#aaaaaa').pack(side=tk.LEFT)
        self.next_label = tk.Label(next_frame, text="", font=('Arial', 9), bg=bg_color, fg='#cccccc', wraplength=200, justify=tk.LEFT)
        self.next_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Elapsed time
        self.time_label = tk.Label(main_frame, text="⏱️ 已运行: 0秒", font=('Arial', 9), bg=bg_color, fg='#ffffff')
        self.time_label.pack(anchor='w', pady=(10, 5))
        
        # Progress bar
        style = ttk.Style()
        try:
             style.theme_use('clam')
        except Exception:
             pass 

        style.configure("Custom.Horizontal.TProgressbar", troughcolor='#333333', background='#00ff88', bordercolor='#444444', lightcolor='#00ff88', darkcolor='#00aa55')
        self.progress_bar = ttk.Progressbar(main_frame, style="Custom.Horizontal.TProgressbar", orient='horizontal', mode='determinate', maximum=100, value=0)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Progress percentage
        self.progress_label = tk.Label(main_frame, text="0%", font=('Arial', 9), bg=bg_color, fg='#aaaaaa')
        self.progress_label.pack(anchor='e')
        
        # ESC hint
        tk.Label(main_frame, text="ESC to cancel", font=('Arial', 8), bg=bg_color, fg='#555555').pack(pady=(5, 0))
        
        # Initial position
        self._update_position()
    
    def _run_overlay(self):
        """Run overlay main loop (persistent thread)"""
        try:
            self._create_window()
            
            # Schedule updates
            self.root.after(100, self._update_loop)
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Overlay thread error: {e}")
            self.running = False
    
    def _update_loop(self):
        """Persistent update loop running on UI thread"""
        if not self.root:
            return

        # Check for shutdown
        if not self.running:
            self.root.quit()
            return
            
        try:
            # 1. Handle Visibility
            if self.should_be_visible and not self.is_visible_actual:
                self.root.deiconify()
                # Re-apply position and topmost in case it got lost
                self._update_position()
                self.root.attributes('-topmost', True)
                self.is_visible_actual = True
                
            elif not self.should_be_visible and self.is_visible_actual:
                self.root.withdraw()
                self.is_visible_actual = False
            
            # 2. Update Content (only if visible or pending)
            if self.is_visible_actual:
                # Update time
                if self.start_time > 0:
                    self.elapsed_time = int(time.time() - self.start_time)
                    if self.time_label:
                        self.time_label.config(text=f"⏱️ 已运行: {self.elapsed_time}秒")

                # Apply data updates
                if self.update_pending:
                    with self.lock:
                        if self.step_label:
                            self.step_label.config(text=f"📍 Step {self.current_step}/{self.total_steps}")
                        if self.current_label:
                            self.current_label.config(text=self.step_description)
                        if self.next_label:
                            self.next_label.config(text=self.next_step_description)
                        if self.progress_bar and self.total_steps > 0:
                            progress = int((self.current_step / self.total_steps) * 100)
                            self.progress_bar['value'] = progress
                            if self.progress_label:
                                self.progress_label.config(text=f"{progress}%")
                        self.update_pending = False

            # Schedule next
            self.root.after(100, self._update_loop)
            
        except Exception as e:
            logger.error(f"Overlay update loop error: {e}")
            # Try to continue
            self.root.after(1000, self._update_loop)
            
    def _update_position(self):
        """Update window position based on config"""
        if not self.root:
            return
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        width, height = self.config.get_dimensions()
        margin = self.config.get_margin()
        
        # Calculate position
        position = self.config.get_position()
        
        if position == OverlayPosition.TOP_RIGHT:
            x = screen_width - width - margin
            y = margin
        elif position == OverlayPosition.TOP_LEFT:
            x = margin
            y = margin
        elif position == OverlayPosition.BOTTOM_RIGHT:
            x = screen_width - width - margin
            y = screen_height - height - margin - 50  # Extra margin for taskbar
        elif position == OverlayPosition.BOTTOM_LEFT:
            x = margin
            y = screen_height - height - margin - 50
        else:
            x = screen_width - width - margin
            y = margin
        
        self.root.geometry(f"+{x}+{y}")
        logger.debug(f"Overlay positioned at ({x}, {y}) - {position.value}")

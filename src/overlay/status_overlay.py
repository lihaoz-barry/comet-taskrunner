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
        self.visible = False
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
    
    def _create_window(self):
        """Create the Tkinter overlay window"""
        if self.root:
            return
        
        self.root = tk.Tk()
        self.root.title("TaskRunner Monitor")
        
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
        
        # Windows-specific: Exclude from screen capture (WDA) & Click-through
        # This makes the overlay invisible to screenshots/videos but visible to user
        # AND allows mouse clicks to pass through to windows below
        try:
            self.root.update()  # Ensure winfo_id is valid
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd:
                # 1. WDA_EXCLUDEFROMCAPTURE = 0x00000011
                WDA_EXCLUDEFROMCAPTURE = 0x00000011
                ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
                logger.info(f"SetWindowDisplayAffinity applied to HWND {hwnd}")

                # 2. Set click-through (WS_EX_TRANSPARENT)
                # GWL_EXSTYLE = -20, WS_EX_LAYERED = 0x80000, WS_EX_TRANSPARENT = 0x20
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x80000
                WS_EX_TRANSPARENT = 0x20
                
                # Get current styles
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                # Add Layered and Transparent styles
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
                logger.info(f"Click-through style applied to HWND {hwnd}")
        except Exception as e:
            logger.warning(f"Failed to set window properties (WDA/Click-through): {e}")
        
        # Set background
        bg_color = '#1a1a1a'
        self.root.configure(bg=bg_color)
        
        # Main frame with padding
        main_frame = tk.Frame(self.root, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title with emoji (Slightly smaller)
        title_label = tk.Label(
            main_frame,
            text="🤖 AI TASK MONITOR",
            font=('Arial', 12, 'bold'),
            bg=bg_color,
            fg='#00ff88'
        )
        title_label.pack(pady=(0, 2))
        
        # Separator
        separator = tk.Frame(main_frame, bg='#444444', height=2)
        separator.pack(fill=tk.X, pady=5)
        
        # Warning text
        warning_label = tk.Label(
            main_frame,
            text="⚡ 屏幕正在被自动控制",
            font=('Arial', 10, 'bold'),
            bg=bg_color,
            fg='#ffaa00'
        )
        warning_label.pack(pady=(5, 10))
        
        # Step info
        self.step_label = tk.Label(
            main_frame,
            text="📍 Step 0/7",
            font=('Arial', 10, 'bold'),
            bg=bg_color,
            fg='#ffffff'
        )
        self.step_label.pack(anchor='w', pady=(5, 3))
        
        # Current step
        current_frame = tk.Frame(main_frame, bg=bg_color)
        current_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            current_frame,
            text="正在:",
            font=('Arial', 9),
            bg=bg_color,
            fg='#aaaaaa'
        ).pack(side=tk.LEFT)
        
        self.current_label = tk.Label(
            current_frame,
            text="等待开始...",
            font=('Arial', 9),
            bg=bg_color,
            fg='#ffffff',
            wraplength=220,
            justify=tk.LEFT
        )
        self.current_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Next step
        next_frame = tk.Frame(main_frame, bg=bg_color)
        next_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            next_frame,
            text="下一步:",
            font=('Arial', 9),
            bg=bg_color,
            fg='#aaaaaa'
        ).pack(side=tk.LEFT)
        
        self.next_label = tk.Label(
            next_frame,
            text="",
            font=('Arial', 9),
            bg=bg_color,
            fg='#cccccc',
            wraplength=200,
            justify=tk.LEFT
        )
        self.next_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Elapsed time
        self.time_label = tk.Label(
            main_frame,
            text="⏱️ 已运行: 0秒",
            font=('Arial', 9),
            bg=bg_color,
            fg='#ffffff'
        )
        self.time_label.pack(anchor='w', pady=(10, 5))
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#333333',
            background='#00ff88',
            bordercolor='#444444',
            lightcolor='#00ff88',
            darkcolor='#00aa55'
        )
        
        self.progress_bar = ttk.Progressbar(
            main_frame,
            style="Custom.Horizontal.TProgressbar",
            orient='horizontal',
            mode='determinate',
            maximum=100,
            value=0
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Progress percentage
        self.progress_label = tk.Label(
            main_frame,
            text="0%",
            font=('Arial', 9),
            bg=bg_color,
            fg='#aaaaaa'
        )
        self.progress_label.pack(anchor='e')
        
        # ESC hint
        esc_label = tk.Label(
            main_frame,
            text="ESC to cancel",
            font=('Arial', 8),
            bg=bg_color,
            fg='#555555'
        )
        esc_label.pack(pady=(5, 0))
        
        # Update position
        self._update_position()
        
        logger.info("Overlay window created")
    
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
    
    def show(self):
        """Show the overlay"""
        if not self.running:
            # Start overlay in separate thread
            self.running = True
            self.visible = True
            threading.Thread(target=self._run_overlay, daemon=True).start()
            
            # Start keyboard listener
            if self.cancel_callback:
                self.keyboard_handler.start_listening(self.cancel_callback)
            
            logger.info("Overlay shown")
        elif not self.visible:
            # Just make visible again
            self.visible = True
            if self.root:
                self.root.deiconify()
            logger.info("Overlay unhidden")
    
    def hide(self):
        """Hide the overlay"""
        self.visible = False
        if self.root:
            self.root.withdraw()
        logger.info("Overlay hidden")
    
    def close(self):
        """Close the overlay window"""
        self.running = False
        self.visible = False
        
        # Stop keyboard listener
        self.keyboard_handler.stop_listening()
        
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception as e:
                logger.warning(f"Error closing overlay window: {e}")
            self.root = None
        logger.info("Overlay closed")
    
    def update_status(self, current_step: int = None, total_steps: int = None,
                     step_description: str = None, next_step_description: str = None):
        """
        Update overlay status (thread-safe).
        
        Args:
            current_step: Current step number
            total_steps: Total number of steps
            step_description: Description of current step
            next_step_description: Description of next step
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
        """
        Set callback function for task cancellation.
        
        Args:
            callback: Function to call when ESC is pressed
        """
        self.cancel_callback = callback
    
    def _run_overlay(self):
        """Run overlay main loop (runs in separate thread)"""
        try:
            self._create_window()
            
            # Start time tracking
            self.start_time = time.time()
            
            # Schedule updates
            self.root.after(100, self._update_loop)
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Overlay error: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_loop(self):
        """Update loop for time and pending changes"""
        if not self.running or not self.root:
            return
        
        try:
            # Update elapsed time
            if self.start_time > 0:
                self.elapsed_time = int(time.time() - self.start_time)
                if self.time_label:
                    self.time_label.config(text=f"⏱️ 已运行: {self.elapsed_time}秒")
            
            # Apply pending updates
            if self.update_pending:
                with self.lock:
                    # Update step label
                    if self.step_label:
                        self.step_label.config(text=f"📍 Step {self.current_step}/{self.total_steps}")
                    
                    # Update current step description
                    if self.current_label:
                        self.current_label.config(text=self.step_description)
                    
                    # Update next step description
                    if self.next_label:
                        self.next_label.config(text=self.next_step_description)
                    
                    # Update progress bar
                    if self.progress_bar and self.total_steps > 0:
                        progress = int((self.current_step / self.total_steps) * 100)
                        self.progress_bar['value'] = progress
                        if self.progress_label:
                            self.progress_label.config(text=f"{progress}%")
                    
                    self.update_pending = False
            
            # Schedule next update
            self.root.after(100, self._update_loop)
            
        except Exception as e:
            logger.error(f"Update loop error: {e}")
    
    def change_position(self, position: OverlayPosition):
        """
        Change overlay position.
        
        Args:
            position: New position
        """
        self.config.set_position(position)
        if self.root:
            self._update_position()
        logger.info(f"Overlay position changed to {position.value}")

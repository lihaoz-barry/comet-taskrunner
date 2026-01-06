"""
Tray Controller for Comet Task Runner

Manages system tray icon, menus, and user interactions.
"""

import os
import sys
import logging
import threading
from typing import Optional, Callable
from pathlib import Path

try:
    from PIL import Image
    import pystray
    PYSTRAY_AVAILABLE = True
except ImportError as e:
    PYSTRAY_AVAILABLE = False
    pystray = None
    print(f"pystray not available: {e}")

logger = logging.getLogger(__name__)


class TrayController:
    """System tray controller for backend application"""
    
    def __init__(self, on_show_log: Optional[Callable] = None, on_exit: Optional[Callable] = None):
        """
        Initialize tray controller.
        
        Args:
            on_show_log: Callback when "Show Log" is clicked
            on_exit: Callback when "Exit" is clicked
        """
        self.on_show_log = on_show_log
        self.on_exit = on_exit
        self.icon: Optional[pystray.Icon] = None
        self.running = False
        self._icon_image = None
        
        if not PYSTRAY_AVAILABLE:
            logger.warning("pystray not available - system tray disabled")
    
    def _get_icon_path(self) -> Optional[str]:
        """Get path to icon file, handling both dev and exe modes"""
        # Try several locations
        possible_paths = []
        
        # 1. PyInstaller bundled path
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            possible_paths.append(Path(sys._MEIPASS) / "Resources" / "comet_icon.png")
        
        # 2. Relative to this file (dev mode)
        current_dir = Path(__file__).parent.parent.parent  # src/tray -> src -> project root
        possible_paths.append(current_dir / "Resources" / "comet_icon.png")
        
        # 3. Relative to cwd
        possible_paths.append(Path.cwd() / "Resources" / "comet_icon.png")
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found icon at: {path}")
                return str(path)
        
        logger.warning("Icon file not found, will use generated icon")
        return None
    
    def _load_icon_image(self) -> Image.Image:
        """Load or generate tray icon image"""
        icon_path = self._get_icon_path()
        
        if icon_path:
            try:
                img = Image.open(icon_path)
                # Resize if needed (system tray icons are usually 16x16 to 64x64)
                img = img.resize((64, 64), Image.Resampling.LANCZOS)
                return img
            except Exception as e:
                logger.warning(f"Failed to load icon: {e}")
        
        # Fallback: generate simple icon
        return self._generate_fallback_icon()
    
    def _generate_fallback_icon(self) -> Image.Image:
        """Generate a simple fallback icon if PNG not found"""
        from PIL import ImageDraw
        
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Simple robot head
        draw.rectangle([12, 12, 52, 52], fill='#00CCCC', outline='#008888', width=2)
        draw.rectangle([20, 24, 28, 32], fill='#1a1a1a')  # Left eye
        draw.rectangle([36, 24, 44, 32], fill='#1a1a1a')  # Right eye
        draw.rectangle([24, 40, 40, 44], fill='#1a1a1a')  # Mouth
        
        return image
    
    def _create_menu(self) -> pystray.Menu:
        """Create tray right-click menu"""
        return pystray.Menu(
            pystray.MenuItem(
                "Show Log...",
                self._handle_show_log
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "退出 (Exit)",
                self._handle_exit
            ),
        )
    
    def _handle_show_log(self, icon, item):
        """Handle Show Log menu click"""
        logger.info("Show Log clicked")
        if self.on_show_log:
            # Run callback in separate thread to avoid blocking pystray
            threading.Thread(target=self.on_show_log, daemon=True).start()
        else:
            # Placeholder: Show message that feature is coming
            logger.info("Log window feature coming in Phase 2")
            def show_placeholder_message():
                try:
                    import tkinter as tk
                    from tkinter import messagebox
                    # Create hidden root window
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    messagebox.showinfo(
                        "Comet Task Runner",
                        "日志窗口功能开发中...\n(Log window coming in Phase 2)",
                        parent=root
                    )
                    root.destroy()
                except Exception as e:
                    logger.warning(f"Could not show message box: {e}")
                    # Fallback to print
                    print(f"Show Log clicked! (Dialog failed: {e})")
            # Run in separate thread to avoid blocking
            threading.Thread(target=show_placeholder_message, daemon=True).start()
    
    def _handle_exit(self, icon, item):
        """Handle Exit menu click"""
        logger.info("Exit requested from tray menu")
        self.stop()
        if self.on_exit:
            self.on_exit()
    
    def start(self):
        """Start the system tray icon (blocking)"""
        if not PYSTRAY_AVAILABLE:
            logger.error("Cannot start tray - pystray not available")
            return
        
        if self.running:
            logger.warning("Tray already running")
            return
        
        self.running = True
        self._icon_image = self._load_icon_image()
        
        self.icon = pystray.Icon(
            "comet_taskrunner",
            self._icon_image,
            "Comet Task Runner",
            self._create_menu()
        )
        
        logger.info("Starting system tray icon...")
        # This blocks until stop() is called
        self.icon.run()
    
    def start_async(self):
        """Start the system tray icon in a separate thread"""
        if not PYSTRAY_AVAILABLE:
            logger.error("Cannot start tray - pystray not available")
            return
        
        threading.Thread(target=self.start, daemon=True).start()
        logger.info("System tray started in background thread")
    
    def stop(self):
        """Stop the system tray icon"""
        self.running = False
        if self.icon:
            try:
                self.icon.stop()
                logger.info("System tray stopped")
            except Exception as e:
                logger.warning(f"Error stopping tray: {e}")
    
    def update_tooltip(self, text: str):
        """Update tray icon tooltip text"""
        if self.icon:
            self.icon.title = text

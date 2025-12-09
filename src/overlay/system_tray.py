"""
System Tray Icon

Provides system tray icon with menu for overlay control.
"""

import logging
import threading
from typing import Optional, Callable
from PIL import Image, ImageDraw

try:
    import pystray
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logging.warning("pystray not available - system tray will be disabled")

from .overlay_config import OverlayPosition

logger = logging.getLogger(__name__)


class SystemTray:
    """System tray icon manager"""
    
    def __init__(self, overlay_controller=None):
        """
        Initialize system tray.
        
        Args:
            overlay_controller: StatusOverlay instance to control
        """
        self.overlay_controller = overlay_controller
        self.icon: Optional[pystray.Icon] = None
        self.running = False
        
        if not PYSTRAY_AVAILABLE:
            logger.warning("System tray not available (pystray not installed)")
    
    def create_icon_image(self):
        """Create a simple icon image"""
        # Create a 64x64 image with a robot emoji-like icon
        size = 64
        image = Image.new('RGB', (size, size), color='#1a1a1a')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple robot head shape
        # Head outline
        draw.rectangle([12, 12, 52, 52], fill='#00ff88', outline='#00aa55', width=2)
        
        # Eyes
        draw.rectangle([20, 24, 28, 32], fill='#1a1a1a')
        draw.rectangle([36, 24, 44, 32], fill='#1a1a1a')
        
        # Mouth
        draw.rectangle([24, 40, 40, 44], fill='#1a1a1a')
        
        return image
    
    def start(self):
        """Start system tray icon"""
        if not PYSTRAY_AVAILABLE:
            logger.info("System tray disabled (pystray not available)")
            return
        
        if self.running:
            return
        
        self.running = True
        
        # Create icon in separate thread
        threading.Thread(target=self._run_tray, daemon=True).start()
        logger.info("System tray started")
    
    def stop(self):
        """Stop system tray icon"""
        self.running = False
        if self.icon:
            try:
                self.icon.stop()
            except:
                pass
        logger.info("System tray stopped")
    
    def _run_tray(self):
        """Run system tray (runs in separate thread)"""
        try:
            icon_image = self.create_icon_image()
            
            menu = self._create_menu()
            
            self.icon = pystray.Icon(
                "comet_automation",
                icon_image,
                "COMET Automation",
                menu
            )
            
            self.icon.run()
            
        except Exception as e:
            logger.error(f"System tray error: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_menu(self):
        """Create tray menu"""
        if not PYSTRAY_AVAILABLE:
            return None
        
        return pystray.Menu(
            pystray.MenuItem(
                "显示 Overlay",
                self._toggle_overlay,
                checked=lambda item: self._is_overlay_visible()
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "位置设置",
                pystray.Menu(
                    pystray.MenuItem(
                        "左上角",
                        self._set_position_top_left,
                        checked=lambda item: self._is_position(OverlayPosition.TOP_LEFT)
                    ),
                    pystray.MenuItem(
                        "右上角",
                        self._set_position_top_right,
                        checked=lambda item: self._is_position(OverlayPosition.TOP_RIGHT)
                    ),
                    pystray.MenuItem(
                        "左下角",
                        self._set_position_bottom_left,
                        checked=lambda item: self._is_position(OverlayPosition.BOTTOM_LEFT)
                    ),
                    pystray.MenuItem(
                        "右下角",
                        self._set_position_bottom_right,
                        checked=lambda item: self._is_position(OverlayPosition.BOTTOM_RIGHT)
                    ),
                )
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "当前状态: 空闲",
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "退出",
                self._exit_app
            ),
        )
    
    def _toggle_overlay(self, icon, item):
        """Toggle overlay visibility"""
        if self.overlay_controller:
            if self._is_overlay_visible():
                self.overlay_controller.hide()
            else:
                self.overlay_controller.show()
    
    def _is_overlay_visible(self):
        """Check if overlay is visible"""
        if self.overlay_controller:
            return self.overlay_controller.visible
        return False
    
    def _set_position_top_left(self, icon, item):
        """Set overlay to top left"""
        if self.overlay_controller:
            self.overlay_controller.change_position(OverlayPosition.TOP_LEFT)
    
    def _set_position_top_right(self, icon, item):
        """Set overlay to top right"""
        if self.overlay_controller:
            self.overlay_controller.change_position(OverlayPosition.TOP_RIGHT)
    
    def _set_position_bottom_left(self, icon, item):
        """Set overlay to bottom left"""
        if self.overlay_controller:
            self.overlay_controller.change_position(OverlayPosition.BOTTOM_LEFT)
    
    def _set_position_bottom_right(self, icon, item):
        """Set overlay to bottom right"""
        if self.overlay_controller:
            self.overlay_controller.change_position(OverlayPosition.BOTTOM_RIGHT)
    
    def _is_position(self, position: OverlayPosition):
        """Check if overlay is at given position"""
        if self.overlay_controller:
            return self.overlay_controller.config.get_position() == position
        return False
    
    def _exit_app(self, icon, item):
        """Exit application"""
        logger.info("Exit requested from system tray")
        self.stop()
        if self.overlay_controller:
            self.overlay_controller.close()

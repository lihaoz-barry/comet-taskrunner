"""
Overlay Configuration Management

Manages overlay position settings and persistence.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class OverlayPosition(Enum):
    """Overlay position options"""
    TOP_RIGHT = "top_right"
    TOP_LEFT = "top_left"
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_LEFT = "bottom_left"


class OverlayConfig:
    """Configuration manager for overlay settings"""
    
    DEFAULT_CONFIG = {
        'position': OverlayPosition.TOP_RIGHT.value,
        'visible': True,
        'opacity': 0.85,
        'width': 300,
        'height': 280,
        'margin': 20,
    }
    
    def __init__(self, config_file: str = None):
        """
        Initialize config manager.
        
        Args:
            config_file: Optional custom config file path
        """
        if config_file:
            self.config_file = Path(config_file)
        else:
            # Default to project root config directory
            self.config_file = Path(__file__).parent.parent.parent / "config" / "overlay_config.json"
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"Loaded overlay config from {self.config_file}")
                    return {**self.DEFAULT_CONFIG, **config}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                return self.DEFAULT_CONFIG.copy()
        else:
            logger.info("No config file found, using defaults")
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved overlay config to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get_position(self) -> OverlayPosition:
        """Get overlay position"""
        try:
            return OverlayPosition(self.config['position'])
        except (KeyError, ValueError):
            return OverlayPosition.TOP_RIGHT
    
    def set_position(self, position: OverlayPosition):
        """Set overlay position and save"""
        self.config['position'] = position.value
        self.save_config()
    
    def is_visible(self) -> bool:
        """Check if overlay should be visible"""
        return self.config.get('visible', True)
    
    def set_visible(self, visible: bool):
        """Set visibility and save"""
        self.config['visible'] = visible
        self.save_config()
    
    def get_opacity(self) -> float:
        """Get overlay opacity (0.0 to 1.0)"""
        return self.config.get('opacity', 0.85)
    
    def get_dimensions(self) -> tuple:
        """Get overlay dimensions (width, height)"""
        return (self.config.get('width', 300), self.config.get('height', 280))
    
    def get_margin(self) -> int:
        """Get margin from screen edge"""
        return self.config.get('margin', 20)

"""
点击位置计算器

支持在匹配框内计算不同的点击位置：
- 预定义位置 (top-left, center, bottom-right等)
- 百分比偏移 (x: 10%, y: 50%)
- 像素偏移 (x_offset: -50, y_offset: 10)
"""

from typing import Union, Tuple, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ClickPosition:
    """计算匹配框内的点击位置"""
    
    # 预定义位置映射 (x_ratio, y_ratio)
    PRESETS = {
        'top-left': (0.0, 0.0),
        'top-center': (0.5, 0.0),
        'top-right': (1.0, 0.0),
        'middle-left': (0.0, 0.5),
        'center': (0.5, 0.5),
        'middle-right': (1.0, 0.5),
        'bottom-left': (0.0, 1.0),
        'bottom-center': (0.5, 1.0),
        'bottom-right': (1.0, 1.0)
    }
    
    @staticmethod
    def calculate(
        match_box: Tuple[int, int, int, int],
        window_rect: Tuple[int, int, int, int],
        position_config: Union[str, Dict[str, Any], None] = None
    ) -> Tuple[int, int]:
        """
        计算实际点击的屏幕坐标
        
        Args:
            match_box: 匹配框在截图中的位置 (x, y, width, height)
            window_rect: 窗口在屏幕上的位置 (left, top, right, bottom)
            position_config: 点击位置配置
                - None 或 'center': 中心点 (默认)
                - str: 预定义位置 'top-left', 'bottom-right' 等
                - dict: {'x': '10%', 'y': '50%'} 或 {'x_offset': -50, 'y_offset': 10}
                
        Returns:
            (screen_x, screen_y) 屏幕坐标
            
        Examples:
            >>> # 中心点 (默认)
            >>> calculate((100, 200, 50, 30), (0, 0, 1920, 1080))
            (125, 215)
            
            >>> # 左上角
            >>> calculate((100, 200, 50, 30), (0, 0, 1920, 1080), 'top-left')
            (100, 200)
            
            >>> # 百分比
            >>> calculate((100, 200, 50, 30), (0, 0, 1920, 1080), {'x': '10%', 'y': '50%'})
            (105, 215)
        """
        match_x, match_y, match_w, match_h = match_box
        win_left, win_top = window_rect[:2]
        
        # 默认中心点
        if not position_config or position_config == 'center':
            rel_x = match_x + match_w // 2
            rel_y = match_y + match_h // 2
            logger.debug(f"Using default center position: ({rel_x}, {rel_y})")
            
        # 预定义位置
        elif isinstance(position_config, str):
            if position_config in ClickPosition.PRESETS:
                x_ratio, y_ratio = ClickPosition.PRESETS[position_config]
                rel_x = match_x + int(match_w * x_ratio)
                rel_y = match_y + int(match_h * y_ratio)
                logger.info(f"Using preset '{position_config}': ratio=({x_ratio}, {y_ratio}), pos=({rel_x}, {rel_y})")
            else:
                logger.warning(f"Unknown preset '{position_config}', falling back to center")
                rel_x = match_x + match_w // 2
                rel_y = match_y + match_h // 2
        
        # 字典配置
        elif isinstance(position_config, dict):
            rel_x, rel_y = ClickPosition._calculate_from_dict(
                match_x, match_y, match_w, match_h, position_config
            )
        else:
            logger.warning(f"Invalid position_config type: {type(position_config)}, using center")
            rel_x = match_x + match_w // 2
            rel_y = match_y + match_h // 2
        
        # 转换为屏幕坐标
        screen_x = win_left + rel_x
        screen_y = win_top + rel_y
        
        logger.debug(f"Final screen coordinates: ({screen_x}, {screen_y})")
        return (screen_x, screen_y)
    
    @staticmethod
    def _calculate_from_dict(
        match_x: int,
        match_y: int,
        match_w: int,
        match_h: int,
        config: Dict[str, Any]
    ) -> Tuple[int, int]:
        """从字典配置计算相对位置"""
        
        # 优先使用 x, y 百分比或比例
        if 'x' in config and 'y' in config:
            x_val = config['x']
            y_val = config['y']
            
            # 解析 x
            if isinstance(x_val, str) and x_val.endswith('%'):
                x_ratio = float(x_val.rstrip('%')) / 100
            elif isinstance(x_val, (int, float)):
                x_ratio = float(x_val) if x_val <= 1.0 else x_val / 100
            else:
                x_ratio = 0.5
                
            # 解析 y
            if isinstance(y_val, str) and y_val.endswith('%'):
                y_ratio = float(y_val.rstrip('%')) / 100
            elif isinstance(y_val, (int, float)):
                y_ratio = float(y_val) if y_val <= 1.0 else y_val / 100
            else:
                y_ratio = 0.5
            
            rel_x = match_x + int(match_w * x_ratio)
            rel_y = match_y + int(match_h * y_ratio)
            logger.info(f"Using percentage position: x={x_ratio*100}%, y={y_ratio*100}%, pos=({rel_x}, {rel_y})")
            
        # 使用 x_offset, y_offset 像素偏移 (相对中心)
        elif 'x_offset' in config or 'y_offset' in config:
            base_x = match_x + match_w // 2
            base_y = match_y + match_h // 2
            
            x_off = config.get('x_offset', 0)
            y_off = config.get('y_offset', 0)
            
            rel_x = base_x + x_off
            rel_y = base_y + y_off
            logger.info(f"Using pixel offset: offset=({x_off}, {y_off}), pos=({rel_x}, {rel_y})")
        else:
            # 默认中心
            rel_x = match_x + match_w // 2
            rel_y = match_y + match_h // 2
            logger.debug(f"No valid config in dict, using center: ({rel_x}, {rel_y})")
        
        return (rel_x, rel_y)
    
    @staticmethod
    def get_available_presets() -> list:
        """返回所有可用的预定义位置"""
        return list(ClickPosition.PRESETS.keys())

# Overlay Module

桌面状态 Overlay 系统，用于在自动化任务运行时显示实时状态。

## 快速开始

```python
from overlay import StatusOverlay

# 创建并显示 Overlay
overlay = StatusOverlay()
overlay.show()

# 更新状态
overlay.update_status(
    current_step=1,
    total_steps=7,
    step_description="等待浏览器初始化",
    next_step_description="激活窗口"
)

# 关闭
overlay.close()
```

## 模块组成

- **`StatusOverlay`**: Tkinter 桌面 Overlay 窗口
- **`OverlayConfig`**: 配置管理（位置、透明度等）
- **`OverlayPosition`**: 位置枚举（TOP_RIGHT, TOP_LEFT, etc.）
- **`SystemTray`**: 系统托盘图标（可选）
- **`KeyboardHandler`**: ESC 键监听（可选）

## 示例

查看项目根目录下的示例文件：
- `demo_overlay.py` - 快速演示
- `test_overlay.py` - 完整测试套件

## 文档

详细文档请参考：`docs/OVERLAY_SYSTEM.md`

## 集成

Overlay 系统已自动集成到 `AITask` 中，无需手动调用。

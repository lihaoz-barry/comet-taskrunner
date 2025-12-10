# Overlay System Quick Reference

## 🚀 Quick Start

```bash
# Run demo
python demo_overlay.py

# Run tests
python test_overlay.py
```

## 📦 Module Structure

```
src/overlay/
├── overlay_config.py      # Configuration & persistence
├── status_overlay.py      # Main Tkinter window
├── system_tray.py         # System tray icon
├── keyboard_handler.py    # ESC key monitoring
└── __init__.py           # Module exports
```

## 💻 Basic Usage

```python
from overlay import StatusOverlay

# Create overlay
overlay = StatusOverlay()

# Show it
overlay.show()

# Update status
overlay.update_status(
    current_step=3,
    total_steps=7,
    step_description="查找输入框",
    next_step_description="输入指令文字"
)

# Close it
overlay.close()
```

## 🎨 UI Elements

| Element | Description |
|---------|-------------|
| 🤖 Title | "COMET AUTOMATION" |
| ⚡ Warning | "屏幕正在被自动控制" |
| 📍 Step | "Step X/7" |
| Current | What's happening now |
| Next | What's coming next |
| ⏱️ Timer | Elapsed time counter |
| Progress | Visual progress bar |
| ESC Hint | Cancellation reminder |

## 📍 Positions

```python
from overlay import OverlayPosition

OverlayPosition.TOP_RIGHT    # Default
OverlayPosition.TOP_LEFT
OverlayPosition.BOTTOM_RIGHT
OverlayPosition.BOTTOM_LEFT
```

## ⚙️ Configuration

Config file: `config/overlay_config.json`

```json
{
  "position": "top_right",
  "visible": true,
  "opacity": 0.85,
  "width": 300,
  "height": 280,
  "margin": 20
}
```

## 🔑 Key Features

- ✅ Always on top
- ✅ Semi-transparent (85%)
- ✅ Borderless window
- ✅ Real-time updates (100ms)
- ✅ Thread-safe
- ✅ Position memory
- ✅ ESC to cancel
- ✅ System tray support

## 🔧 AITask Integration

Automatic! No code needed:

```python
from tasks import AITask

task = AITask("your instruction")
task.execute(comet_path="path/to/comet.exe")
# Overlay shows automatically!
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Overlay not showing | Install python3-tk |
| Tray not working | GTK not available (optional) |
| ESC not working | keyboard module needs admin rights |

## 📚 Documentation

- **Full docs**: `docs/OVERLAY_SYSTEM.md`
- **Implementation**: `OVERLAY_IMPLEMENTATION_SUMMARY.md`
- **UI mockup**: `docs/overlay_ui_mockup.txt`
- **Module README**: `src/overlay/README.md`

## 🎯 Dependencies

**Required:**
- `tkinter` (Python built-in, install python3-tk)

**Optional:**
- `pystray` - System tray (needs GTK)
- `keyboard` - ESC key (needs admin)
- `Pillow` - Images (auto-installed with pystray)

## 📊 Statistics

- **Code**: 793 lines (5 modules)
- **Tests**: 263 lines (2 scripts)
- **Docs**: 730+ lines (4 files)
- **Total**: 1,800+ lines

## ✅ Status

All features implemented and tested!
- ✅ Core functionality
- ✅ AITask integration
- ✅ Tests & demos
- ✅ Documentation
- ✅ Code review passed
- ✅ Security scan passed

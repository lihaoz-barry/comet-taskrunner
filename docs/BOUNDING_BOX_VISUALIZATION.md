# Bounding Box Visualization Feature

## Overview

The bounding box visualization feature provides real-time visual feedback when widgets are detected during automation tasks. When a widget is successfully detected, a red rectangular frame appears at the exact location with a smooth gradient fade-in/out animation.

## Features

- **Red Rectangular Frame**: Clear visual indication at the detected widget location
- **Gradient Animation**: Smooth fade-in and fade-out transitions (0.3s each)
- **Brief Display**: Shows at full opacity for 0.5s between fade transitions
- **Non-intrusive**: Click-through transparent overlay that doesn't interfere with automation
- **Auto-cleanup**: Automatically disappears after animation completes

## Implementation Details

### BoundingBoxOverlay Class

Located in `src/overlay/bounding_box_overlay.py`, this class provides:

- **Transparent overlay window** using tkinter
- **Always-on-top** positioning to ensure visibility
- **Click-through** functionality (Windows) to avoid blocking automation
- **Thread-safe** animation handling

### Animation Configuration

```python
FADE_IN_DURATION = 0.3   # seconds
FADE_OUT_DURATION = 0.3  # seconds
DISPLAY_DURATION = 0.5   # seconds at full opacity
FRAME_INTERVAL = 0.02    # 50 FPS for smooth animation
```

### Integration Points

The bounding box overlay is automatically triggered in:

1. **DetectAction** (`src/workflow/actions/detect_action.py`)
   - Shows bounding box when template matching succeeds
   - Displays at the exact screen coordinates of the detected widget

2. **DetectLoopAction** (`src/workflow/actions/detect_loop_action.py`)
   - Shows bounding box when widget appears (in `wait_until_appears` mode)
   - Provides visual confirmation during monitoring loops

## Usage

### Automatic Usage

The bounding box visualization is automatically displayed when:
- A `detect` action successfully finds a widget
- A `detect_loop` action detects widget appearance

No configuration required - works out of the box!

### Manual Usage (Advanced)

```python
from overlay import BoundingBoxOverlay

# Create overlay instance
overlay = BoundingBoxOverlay()

# Show bounding box at screen coordinates
# x, y: top-left corner
# width, height: dimensions of the box
overlay.show_bounding_box(x=500, y=300, width=200, height=150)
```

## Testing

Run the test script to see the animation in action:

```bash
python test_bounding_box.py
```

This will display several animated bounding boxes at different screen positions to demonstrate the gradient fade effect.

## Technical Notes

### Animation Flow

1. **Create Window**: Transparent tkinter window at target coordinates
2. **Fade In**: Opacity gradually increases from 0.0 to 1.0 over 0.3s
3. **Display**: Shows at full opacity for 0.5s
4. **Fade Out**: Opacity gradually decreases from 1.0 to 0.0 over 0.3s
5. **Cleanup**: Window is destroyed automatically

### Thread Safety

- Each bounding box animation runs in a separate thread
- Thread-safe window creation and destruction
- Non-blocking - doesn't interfere with automation workflow

### Platform Compatibility

- **Windows**: Full support including click-through functionality
- **Linux**: Core functionality supported (click-through may not work)
- **macOS**: Core functionality supported (click-through may not work)

## Troubleshooting

### Box not appearing

- Check that widget detection is successful (check logs)
- Verify screen coordinates are within visible screen bounds
- Ensure tkinter is properly installed

### Animation stuttering

- The frame interval can be adjusted in `BoundingBoxOverlay.FRAME_INTERVAL`
- Lower FPS may help on slower systems

### Overlapping animations

- If detection happens very quickly, overlays are skipped to prevent visual clutter
- Each overlay completes its animation before cleanup

## Future Enhancements

Potential improvements for future versions:

- Configurable box color and border width
- Different animation styles (pulse, flash, etc.)
- Optional sound feedback
- Persistent mode for debugging
- Multiple box support for batch detections

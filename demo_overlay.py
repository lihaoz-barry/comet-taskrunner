"""
Simple Overlay Demo

Quick demonstration of overlay functionality.
Run this to see the overlay in action.
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from overlay import StatusOverlay

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run simple overlay demonstration"""
    logger.info("Starting Overlay Demo...")
    logger.info("The overlay will appear in the top-right corner")
    logger.info("It will simulate a 7-step automation sequence")
    logger.info("Press ESC to cancel (if keyboard module is available)")
    
    # Create overlay
    overlay = StatusOverlay()
    
    # Set cancel callback
    def on_cancel():
        logger.info("✗ Task cancelled by user!")
        overlay.close()
        sys.exit(0)
    
    overlay.set_cancel_callback(on_cancel)
    
    # Show overlay
    overlay.show()
    time.sleep(1)  # Wait for overlay to appear
    
    # Simulate automation steps
    steps = [
        ("等待浏览器初始化", "激活窗口"),
        ("激活Comet窗口", "查找Assistant按钮"),
        ("查找Assistant按钮", "点击Assistant按钮"),
        ("点击Assistant按钮", "查找输入框"),
        ("查找输入框", "输入指令文字"),
        ("输入指令文字", "发送指令"),
        ("发送指令", "完成"),
    ]
    
    try:
        for i, (current, next_step) in enumerate(steps, 1):
            logger.info(f"Step {i}/7: {current}")
            overlay.update_status(
                current_step=i,
                total_steps=7,
                step_description=current,
                next_step_description=next_step if i < 7 else ""
            )
            time.sleep(3)  # Simulate step execution
        
        logger.info("✓ All steps completed!")
        time.sleep(2)
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted")
    finally:
        overlay.close()
        logger.info("Demo finished")


if __name__ == "__main__":
    main()

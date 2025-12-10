"""
Quick automated test for overlay system
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from overlay import StatusOverlay, OverlayConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Quick test of overlay"""
    logger.info("="*60)
    logger.info("Quick Overlay Test")
    logger.info("="*60)

    try:
        # Create overlay
        logger.info("Creating overlay...")
        overlay = StatusOverlay()

        # Show overlay
        logger.info("Showing overlay window...")
        overlay.show()

        # Wait for window to appear
        time.sleep(1)

        # Simulate some automation steps
        logger.info("Simulating automation steps...")
        steps = [
            ("等待浏览器初始化", "激活窗口"),
            ("激活Comet窗口", "查找Assistant按钮"),
            ("查找Assistant按钮", "点击按钮"),
        ]

        for i, (current, next_step) in enumerate(steps, 1):
            logger.info(f"  Step {i}: {current}")
            overlay.update_status(
                current_step=i,
                total_steps=7,
                step_description=current,
                next_step_description=next_step
            )
            time.sleep(1.5)

        logger.info("Keeping overlay visible for 3 seconds...")
        time.sleep(3)

        # Close overlay
        logger.info("Closing overlay...")
        overlay.close()

        logger.info("✓ Overlay test completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"✗ Overlay test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Test Script for Overlay System

Demonstrates the overlay functionality without running actual automation.
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from overlay import StatusOverlay, OverlayConfig, OverlayPosition, SystemTray

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_overlay_basic():
    """Test basic overlay functionality"""
    logger.info("="*60)
    logger.info("Testing Overlay System - Basic Functionality")
    logger.info("="*60)
    
    # Create overlay
    overlay = StatusOverlay()
    
    def cancel_handler():
        logger.info("Cancel handler called!")
        overlay.close()
    
    overlay.set_cancel_callback(cancel_handler)
    
    # Show overlay
    logger.info("Showing overlay...")
    overlay.show()
    
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
    
    for i, (current, next_step) in enumerate(steps, 1):
        logger.info(f"Step {i}/7: {current}")
        overlay.update_status(
            current_step=i,
            total_steps=7,
            step_description=current,
            next_step_description=next_step
        )
        time.sleep(2)  # Simulate step execution time
    
    logger.info("All steps completed!")
    time.sleep(2)
    
    # Close overlay
    logger.info("Closing overlay...")
    overlay.close()
    
    logger.info("Test completed successfully!")


def test_overlay_positions():
    """Test different overlay positions"""
    logger.info("="*60)
    logger.info("Testing Overlay Positions")
    logger.info("="*60)
    
    positions = [
        OverlayPosition.TOP_RIGHT,
        OverlayPosition.TOP_LEFT,
        OverlayPosition.BOTTOM_RIGHT,
        OverlayPosition.BOTTOM_LEFT,
    ]
    
    for position in positions:
        logger.info(f"Testing position: {position.value}")
        
        config = OverlayConfig()
        config.set_position(position)
        
        overlay = StatusOverlay(config)
        overlay.update_status(
            current_step=3,
            total_steps=7,
            step_description=f"测试位置: {position.value}",
            next_step_description="下一步测试"
        )
        
        overlay.show()
        time.sleep(3)
        overlay.close()
        time.sleep(1)
    
    logger.info("Position test completed!")


def test_with_system_tray():
    """Test overlay with system tray"""
    logger.info("="*60)
    logger.info("Testing Overlay with System Tray")
    logger.info("="*60)
    logger.info("Note: System tray may not work in headless environment")
    
    # Create overlay
    overlay = StatusOverlay()
    
    # Create system tray
    tray = SystemTray(overlay)
    
    # Start tray
    tray.start()
    
    # Show overlay
    overlay.show()
    
    # Simulate some work
    for i in range(1, 8):
        overlay.update_status(
            current_step=i,
            total_steps=7,
            step_description=f"执行步骤 {i}",
            next_step_description=f"准备步骤 {i+1}"
        )
        time.sleep(2)
    
    # Keep running for a bit to allow tray interaction
    logger.info("Overlay and tray running... Press Ctrl+C to exit")
    try:
        time.sleep(20)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    # Cleanup
    overlay.close()
    tray.stop()
    
    logger.info("System tray test completed!")


def main():
    """Main test function"""
    logger.info("Overlay System Test Suite")
    logger.info("Choose a test:")
    logger.info("1. Basic overlay functionality")
    logger.info("2. Test different positions")
    logger.info("3. Test with system tray")
    logger.info("4. Run all tests")
    
    try:
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            test_overlay_basic()
        elif choice == "2":
            test_overlay_positions()
        elif choice == "3":
            test_with_system_tray()
        elif choice == "4":
            test_overlay_basic()
            time.sleep(2)
            test_overlay_positions()
            time.sleep(2)
            test_with_system_tray()
        else:
            logger.error("Invalid choice")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Test script for BoundingBoxOverlay

Demonstrates the gradient fade-in/out animation for widget detection visualization.
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from overlay import BoundingBoxOverlay

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test the bounding box overlay with gradient animation"""
    logger.info("Starting BoundingBoxOverlay Test")
    logger.info("=" * 60)
    logger.info("This test will display animated red bounding boxes")
    logger.info("at different screen positions to demonstrate the")
    logger.info("gradient fade-in/out animation effect.")
    logger.info("=" * 60)
    
    # Test 1: Center of screen
    logger.info("\nTest 1: Center of screen (300x200 box)")
    overlay1 = BoundingBoxOverlay()
    overlay1.show_bounding_box(500, 300, 300, 200)
    time.sleep(2)  # Wait for animation to complete
    
    # Test 2: Top-left corner
    logger.info("\nTest 2: Top-left corner (200x150 box)")
    overlay2 = BoundingBoxOverlay()
    overlay2.show_bounding_box(100, 100, 200, 150)
    time.sleep(2)
    
    # Test 3: Bottom-right area
    logger.info("\nTest 3: Bottom-right area (250x180 box)")
    overlay3 = BoundingBoxOverlay()
    overlay3.show_bounding_box(900, 500, 250, 180)
    time.sleep(2)
    
    # Test 4: Multiple boxes in sequence
    logger.info("\nTest 4: Sequence of boxes (simulating detection)")
    positions = [
        (300, 200, 150, 100),
        (600, 350, 180, 120),
        (450, 250, 200, 150),
    ]
    
    for i, (x, y, w, h) in enumerate(positions, 1):
        logger.info(f"  Box {i}: ({x}, {y}) - {w}x{h}")
        overlay = BoundingBoxOverlay()
        overlay.show_bounding_box(x, y, w, h)
        time.sleep(1.5)  # Small delay between boxes
    
    logger.info("\n" + "=" * 60)
    logger.info("Test completed!")
    logger.info("The gradient fade-in/out animation provides smooth visual")
    logger.info("feedback for widget detection without harsh flickering.")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}", exc_info=True)

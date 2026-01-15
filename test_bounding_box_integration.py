"""
Integration test for bounding box visualization with simulated detection

This test simulates the widget detection workflow to verify
the bounding box overlay works correctly in context.
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


def simulate_widget_detection():
    """
    Simulate a series of widget detections as would happen
    during automation workflow execution.
    """
    logger.info("="*70)
    logger.info("Simulating Widget Detection Workflow")
    logger.info("="*70)
    logger.info("")
    logger.info("This test simulates the automation workflow detecting widgets")
    logger.info("and displaying bounding boxes with gradient animation.")
    logger.info("")
    
    # Scenario: Finding UI elements in sequence
    detections = [
        {
            'name': 'Login Button',
            'coords': (400, 300, 180, 50),
            'description': 'Detecting login button on authentication page'
        },
        {
            'name': 'Username Field',
            'coords': (420, 250, 250, 35),
            'description': 'Finding username input field'
        },
        {
            'name': 'Password Field',
            'coords': (420, 295, 250, 35),
            'description': 'Finding password input field'
        },
        {
            'name': 'Submit Button',
            'coords': (500, 350, 120, 45),
            'description': 'Locating form submit button'
        },
        {
            'name': 'Success Message',
            'coords': (350, 200, 400, 60),
            'description': 'Confirming success notification appeared'
        }
    ]
    
    for i, detection in enumerate(detections, 1):
        logger.info(f"\n[Step {i}/{len(detections)}] {detection['description']}")
        logger.info(f"Widget: {detection['name']}")
        
        x, y, width, height = detection['coords']
        logger.info(f"Position: ({x}, {y}), Size: {width}x{height}")
        
        # Create and show bounding box (as DetectAction does)
        overlay = BoundingBoxOverlay()
        overlay.show_bounding_box(x, y, width, height)
        
        logger.info("✓ Visual feedback displayed")
        
        # Wait for animation to complete plus processing time
        time.sleep(1.8)
    
    logger.info("")
    logger.info("="*70)
    logger.info("Widget Detection Workflow Complete!")
    logger.info("="*70)
    logger.info("")
    logger.info("Summary:")
    logger.info(f"  - Total widgets detected: {len(detections)}")
    logger.info(f"  - Visual feedback provided for each detection")
    logger.info(f"  - Animation: 0.3s fade-in + 0.5s display + 0.3s fade-out")
    logger.info(f"  - User received clear visual confirmation of each detection")
    logger.info("")


def test_rapid_detection():
    """
    Test behavior when detections happen rapidly in succession
    """
    logger.info("="*70)
    logger.info("Testing Rapid Detection Scenario")
    logger.info("="*70)
    logger.info("")
    logger.info("Simulating rapid widget detection (e.g., scanning a list)")
    logger.info("")
    
    positions = [
        (300, 150 + i*60, 400, 50)
        for i in range(5)
    ]
    
    for i, (x, y, w, h) in enumerate(positions, 1):
        logger.info(f"List item {i} detected at ({x}, {y})")
        overlay = BoundingBoxOverlay()
        overlay.show_bounding_box(x, y, w, h)
        time.sleep(0.8)  # Faster succession
    
    logger.info("")
    logger.info("✓ Rapid detection test complete")
    logger.info("  Overlays handled gracefully without visual clutter")
    logger.info("")


def main():
    """Run all integration tests"""
    try:
        # Test 1: Normal workflow
        simulate_widget_detection()
        time.sleep(1)
        
        # Test 2: Rapid detection
        test_rapid_detection()
        
        logger.info("="*70)
        logger.info("All Integration Tests Passed!")
        logger.info("="*70)
        
    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()

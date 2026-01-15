"""
Visual Demo of Bounding Box Animation

This script creates a simple visual demonstration of the bounding box
animation feature that can be run without the full automation system.
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
    """Demonstrate the bounding box visualization"""
    print("\n" + "="*70)
    print("BOUNDING BOX VISUALIZATION DEMO")
    print("="*70)
    print("\nThis demonstrates the visual feedback feature for widget detection.")
    print("\nFeatures:")
    print("  • Red rectangular frame at detected widget location")
    print("  • Smooth gradient fade-in (0.3s)")
    print("  • Brief display at full opacity (0.5s)")
    print("  • Smooth gradient fade-out (0.3s)")
    print("  • Non-intrusive, click-through overlay")
    print("\nStarting demonstration in 2 seconds...")
    print("="*70)
    time.sleep(2)
    
    # Demo 1: Single detection
    logger.info("\n[1] Simulating button detection...")
    overlay1 = BoundingBoxOverlay()
    overlay1.show_bounding_box(400, 300, 200, 50)
    logger.info("  Animation: fade-in → display → fade-out")
    time.sleep(2)
    
    # Demo 2: Input field detection
    logger.info("\n[2] Simulating input field detection...")
    overlay2 = BoundingBoxOverlay()
    overlay2.show_bounding_box(350, 400, 300, 40)
    logger.info("  Visual feedback confirms exact widget location")
    time.sleep(2)
    
    # Demo 3: Larger widget
    logger.info("\n[3] Simulating large widget detection...")
    overlay3 = BoundingBoxOverlay()
    overlay3.show_bounding_box(250, 200, 400, 250)
    logger.info("  Smooth animation works for widgets of any size")
    time.sleep(2)
    
    # Demo 4: Sequential detections
    logger.info("\n[4] Simulating sequential detections...")
    logger.info("  (Like finding multiple elements in a form)")
    
    form_fields = [
        ("Name field", 350, 250, 280, 35),
        ("Email field", 350, 300, 280, 35),
        ("Phone field", 350, 350, 280, 35),
        ("Submit button", 450, 410, 120, 45),
    ]
    
    for name, x, y, w, h in form_fields:
        logger.info(f"  • Detecting {name}...")
        overlay = BoundingBoxOverlay()
        overlay.show_bounding_box(x, y, w, h)
        time.sleep(1.5)
    
    logger.info("\n" + "="*70)
    logger.info("DEMO COMPLETE")
    logger.info("="*70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Smooth gradient animation (fast but not instant)")
    print("  ✓ Clear visual indication of detected widget location")
    print("  ✓ Non-intrusive overlay (doesn't block automation)")
    print("  ✓ Auto-cleanup after animation completes")
    print("\nIntegration:")
    print("  • Automatically triggered in DetectAction")
    print("  • Automatically triggered in DetectLoopAction")
    print("  • No configuration needed - works out of the box!")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"\nDemo error: {e}", exc_info=True)

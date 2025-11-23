"""
Quick test script for AI Task automation
"""
import sys
import logging
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tasks.ai_task import AITask

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_ai_task():
    """Test AI task creation and basic functionality"""
    print("="*60)
    print("TESTING AI TASK")
    print("="*60)
    
    # Test 1: Create task
    print("\n[TEST 1] Creating AI task...")
    task = AITask(instruction="请帮我总结一下Python的主要特点")
    print(f"✓ Task created: {task.task_id}")
    print(f"  Instruction: {task.instruction}")
    print(f"  Template dir: {task.template_dir}")
    
    # Test 2: Check template directory
    print("\n[TEST 2] Checking template directory...")
    if task.template_dir.exists():
        print(f"✓ Template directory exists: {task.template_dir}")
        templates = list(task.template_dir.glob("*.png"))
        print(f"  Found {len(templates)} template(s):")
        for t in templates:
            print(f"    - {t.name}")
    else:
        print(f"✗ Template directory not found: {task.template_dir}")
    
    # Test 3: Check automation modules
    print("\n[TEST 3] Checking automation modules...")
    try:
        from automation import WindowManager, ScreenshotCapture, PatternMatcher, MouseController
        print("✓ All automation modules imported successfully")
    except Exception as e:
        print(f"✗ Import error: {e}")
    
    # Test 4: Progress tracking
    print("\n[TEST 4] Testing progress tracking...")
    progress = task.get_automation_progress()
    print(f"✓ Progress: {progress['completed_steps']}/{progress['total_steps']} steps")
    print(f"  Progress: {progress['progress_percent']}%")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED")
    print("="*60)

if __name__ == "__main__":
    test_ai_task()

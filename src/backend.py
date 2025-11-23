"""
Comet Task Runner - Backend API Server

This Flask server provides REST API endpoints for task execution.

It integrates the independent Task components (tasks package) with Flask.
The Task components themselves have NO dependency on Flask.

Architecture:
    Flask API (backend.py)
        ↓ uses
    TaskManager (task_manager.py)
        ↓ stores
    Task Components (tasks/)
        ├── URLTask
        └── AITask

Each layer is independent and can be replaced/reused.
"""

import os
import subprocess
import logging
import winreg
import threading
import time
from flask import Flask, request, jsonify

# Import task components (independent, reusable)
from tasks import BaseTask, TaskStatus, TaskType, URLTask, AITask

# Import task manager (storage layer)
from task_manager import TaskManager

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = Flask(__name__)

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the global Task Manager
# This manages ALL tasks (both URL and AI) in memory
task_manager = TaskManager()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_comet_path():
    """
    Dynamically look up the Comet browser executable path.
    
    Searches in order:
    1. HKCU registry (current user)
    2. HKLM registry (local machine)
    3. Hardcoded fallback path
    
    Returns:
        str: Path to comet.exe or None if not found
    """
    registry_paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\App Paths\comet.exe"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\comet.exe")
    ]

    # Try registry lookups
    for hkey, subkey in registry_paths:
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                path, _ = winreg.QueryValueEx(key, "")
                if path and os.path.exists(path):
                    logger.info(f"Found Comet at: {path}")
                    return path
        except FileNotFoundError:
            continue
        except Exception as e:
            logger.error(f"Registry error: {e}")

    # Fallback to known location
    fallback_path = r"C:\Users\Barry\AppData\Local\Perplexity\Comet\Application\comet.exe"
    if os.path.exists(fallback_path):
        logger.info(f"Using fallback Comet path: {fallback_path}")
        return fallback_path
    
    logger.error("Comet browser not found in registry or fallback location")
    return None


# ============================================================================
# API ENDPOINTS - HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """
    Simple health check endpoint.
    
    Returns:
        200: Server is running
    """
    return jsonify({"status": "ok", "message": "Comet Task Runner is running"}), 200


# ============================================================================
# API ENDPOINTS - URL TASK EXECUTION
# ============================================================================

@app.route('/execute/url', methods=['POST'])
def execute_url():
    """
    Execute a URL navigation task in Comet browser.
    
    Request Body:
        {
            "url": "https://example.com"
        }
    
    Response:
        {
            "status": "started",
            "task_id": "uuid",
            "task_type": "url",
            "process_id": 12345
        }
    
    Workflow:
        1. Validate URL parameter
        2. Check Comet browser availability
        3. Create URLTask object
        4. Execute task (launch browser)
        5. Capture process ID
        6. Start task monitoring
        7. Return task info to client
    """
    # Step 1: Validate input
    data = request.json
    url = data.get('url')
    
    if not url:
        logger.warning("URL task requested without URL parameter")
        return jsonify({"error": "URL is required"}), 400

    # Step 2: Check Comet availability
    comet_path = get_comet_path()
    if not comet_path:
        return jsonify({"error": "Comet browser not found"}), 500

    # Step 3: Create task object
    # This creates a NEW ExecutionJob in memory
    task = task_manager.create_url_task(url)
    logger.info(f"Created URL task {task.task_id} for: {url}")

    try:
        # Step 4 & 5: Execute and capture PID
        process_id = task.execute(comet_path=comet_path)
        
        # Step 6: Start task (sets status to RUNNING)
        task.start(process_id)
        
        logger.info(f"URL task {task.task_id} started with PID {process_id}")
        
        # Step 7: Return success response
        return jsonify({
            "status": "started",
            "task_id": task.task_id,
            "task_type": "url",
            "process_id": process_id,
            "message": "URL task started successfully"
        }), 200
        
    except Exception as e:
        # Handle execution failures
        logger.error(f"Failed to execute URL task: {e}")
        task.fail(str(e))
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINTS - AI TASK EXECUTION (NEW)
# ============================================================================

@app.route('/execute/ai', methods=['POST'])
def execute_ai():
    """
    Execute an AI Assistant interaction task with automation.
    
    Request Body:
        {
            "instruction": "Please summarize this document...",
            "coordinates": {  // Optional coordinate overrides
                "assistant_button": [100, 100],
                "task_input_box": [500, 300],
                "send_button": [800, 500]
            }
        }
    
    Response:
        {
            "status": "started",
            "task_id": "uuid",
            "task_type": "ai",
            "process_id": 12345,
            "instruction": "Please summarize..."
        }
    
    Workflow:
        1. Validate instruction parameter
        2. Check Comet browser availability
        3. Create AITask object
        4. Execute task (launch browser + automation sequence)
        5. Capture process ID
        6. Start task monitoring
        7. Return task info to client
    
    Note:
        The automation sequence runs in a background thread:
        - Click AI Assistant button
        - Click task input box
        - Type instruction
        - Click Send button
        
        These are currently PLACEHOLDERS - see task_manager.py AITask class
    """
    # Step 1: Validate input
    data = request.json
    instruction = data.get('instruction')
    coordinates = data.get('coordinates')  # Optional
    
    if not instruction:
        logger.warning("AI task requested without instruction")
        return jsonify({"error": "instruction is required"}), 400

    # Step 2: Check Comet availability
    comet_path = get_comet_path()
    if not comet_path:
        return jsonify({"error": "Comet browser not found"}), 500

    # Step 3: Create AI task object
    # This creates a NEW AITask in memory with automation logic
    task = task_manager.create_ai_task(instruction, coordinates)
    logger.info(f"Created AI task {task.task_id}: {instruction[:50]}...")

    try:
        # Step 4 & 5: Execute AI automation and capture PID
        # The automation (mouse clicks, typing) happens in a background thread
        process_id = task.execute(comet_path=comet_path)
        
        # Step 6: Start task
        task.start(process_id)
        
        logger.info(f"AI task {task.task_id} started with PID {process_id}")
        
        # Step 7: Return success response
        return jsonify({
            "status": "started",
            "task_id": task.task_id,
            "task_type": "ai",
            "process_id": process_id,
            "instruction": instruction,
            "message": "AI task started, automation sequence initiated"
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to execute AI task: {e}")
        task.fail(str(e))
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINTS - STATUS & MONITORING
# ============================================================================

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """
    Get the current status of any task (URL or AI).
    
    This endpoint is polled by the frontend every ~1 second.
    
    Process:
        1. Look up task by ID
        2. Check task-specific completion logic
        3. Auto-complete if task is done
        4. Return current status
    
    Returns:
        {
            "status": "running" | "done" | "failed",
            "task_id": "uuid",
            "task_type": "url" | "ai",
            "url": "..." or "instruction": "...",
            "process_id": 12345
        }
    """
    # Step 1: Find task
    task = task_manager.get_task(task_id)
    if not task:
        logger.warning(f"Status requested for unknown task: {task_id}")
        return jsonify({"error": "Task ID not found"}), 404
    
    # Step 2 & 3: Check completion using task-specific logic
    # For URLTask: checks if process exited
    # For AITask: checks process + AI detection (placeholder)
    if task.status == TaskStatus.RUNNING and task.check_completion():
        logger.info(f"Auto-completing task {task_id} via status check")
        task.complete()
    
    # Step 4: Return status
    response = {
        "status": task.status.value,
        "task_id": task.task_id,
        "task_type": task.task_type.value,
        "process_id": task.process_id
    }
    
    # Add task-specific fields
    if task.task_type == TaskType.URL:
        response['url'] = task.url
    elif task.task_type == TaskType.AI_ASSISTANT:
        response['instruction'] = task.instruction
    
    return jsonify(response), 200


@app.route('/callback', methods=['POST'])
def callback():
    """
    Manual completion callback endpoint.
    
    Allows browser scripts or external systems to mark tasks as complete.
    
    Request Body:
        {
            "task_id": "uuid",
            "status": "done" | "failed"
        }
    
    Use Cases:
        - Browser script detects AI completion
        - External monitor detects success
        - Manual override
    """
    data = request.json
    task_id = data.get('task_id')
    status = data.get('status')

    if not task_id or not status:
        return jsonify({"error": "task_id and status are required"}), 400

    task = task_manager.get_task(task_id)
    if task:
        task_manager.update_task_status(task_id, status)
        logger.info(f"Task {task_id} updated to '{status}' via callback")
        return jsonify({"status": "updated"}), 200
    else:
        return jsonify({"error": "Task ID not found"}), 404


@app.route('/jobs', methods=['GET'])
def get_all_jobs():
    """
    Get all tasks for debugging/monitoring.
    
    Returns:
        {
            "task_id_1": {
                "task_id": "...",
                "task_type": "url" | "ai",
                "status": "...",
                "process_id": 12345,
                ...
            },
            ...
        }
    """
    return jsonify(task_manager.get_all_tasks()), 200


# ============================================================================
# BACKGROUND MONITORING THREAD
# ============================================================================

def start_task_monitor():
    """
    Background thread to periodically check task completion.
    
    Runs every 5 seconds and calls task_manager.monitor_tasks()
    which checks all RUNNING tasks using their completion logic.
    
    This is especially important for AI tasks that need periodic
    screenshot analysis (placeholder).
    """
    def monitor_loop():
        logger.info("Task monitor thread started")
        while True:
            try:
                task_manager.monitor_tasks()
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            time.sleep(5)  # Check every 5 seconds
    
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()


# ============================================================================
# MAIN APPLICATION ENTRY
# ============================================================================

if __name__ == '__main__':
    import atexit
    from utils.cleanup import cleanup_temp_files
    
    # Register cleanup on normal exit
    atexit.register(cleanup_temp_files)
    
    logger.info("=" * 60)
    logger.info("Starting Comet Task Runner Backend")
    logger.info("=" * 60)
    logger.info("URL Task API: POST /execute/url")
    logger.info("AI Task API:  POST /execute/ai")
    logger.info("Status API:   GET /status/<task_id>")
    logger.info("=" * 60)
    
    # Start background monitoring thread
    start_task_monitor()
    
    try:
        # Start Flask server
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n")
        logger.info("Backend shutting down...")
        cleanup_temp_files()
        logger.info("Goodbye!")

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
import sys
import os

# Add current directory to sys.path to allow imports from src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import subprocess
import logging
import winreg
import threading
import time
from functools import wraps
from flask import Flask, request, jsonify
from dotenv import load_dotenv  # Load .env file
from colorama import init as colorama_init

# Load environment variables from .env file (if present)
load_dotenv()

# Enable ANSI colors and emoji support in Windows console (for exe builds)
colorama_init(autoreset=True)

# Import task components (independent, reusable)
# Import task components (independent, reusable)
from tasks import BaseTask, TaskStatus, TaskType, URLTask, AITask, ConfigurableTask
from workflow import WorkflowRegistry, WorkflowConfig
from pathlib import Path

# Import task manager (storage layer)
from task_manager import TaskManager

# Import task queue (sequential execution manager)
from task_queue import TaskQueue

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = Flask(__name__)

# Authentication Decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1. Localhost Exemption: Allow local requests without key
        if request.remote_addr in ['127.0.0.1', 'localhost', '::1']:
            return f(*args, **kwargs)
            
        # 2. Get Server Key from Environment
        server_key = os.environ.get('COMET_API_KEY')
        
        # Safety check: If exposed but no key set (should be caught at startup, but double check)
        if not server_key:
            logger.error("Security Error: Remote request received but COMET_API_KEY not set")
            return jsonify({"error": "Server configuration error: No API Key set"}), 500

        # 3. Verify Client Key
        client_key = request.headers.get('X-API-Key')
        
        if client_key and client_key == server_key:
            return f(*args, **kwargs)
            
        logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
        return jsonify({"error": "Unauthorized"}), 401
        
    return decorated

# Configure detailed logging
# Configure detailed logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# Use Custom Hybrid Logger
from utils.logger import setup_logging
logger = setup_logging()

# Initialize the global Task Manager
# This manages ALL tasks (both URL and AI) in memory
task_manager = TaskManager()

# Initialize Workflow Registry (load YAML workflows)
# Handle both development and PyInstaller exe modes
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller exe - use _MEIPASS
    base_path = Path(sys._MEIPASS)
    workflows_path = base_path / "workflows"
    logger.info(f"EXE mode: Loading workflows from bundled path: {workflows_path}")
else:
    # Running in development mode - use relative path
    workflows_path = Path(__file__).parent.parent / "workflows"
    logger.info(f"Dev mode: Loading workflows from: {workflows_path}")

workflow_registry = WorkflowRegistry(
    workflows_dir=str(workflows_path)
)

# Initialize Composite Action Registry (load reusable action YAMLs)
from workflow.actions.composite_action import CompositeActionRegistry
composite_actions_path = workflows_path / "actions"
if composite_actions_path.exists():
    CompositeActionRegistry.load_from_directory(str(composite_actions_path))
else:
    logger.info(f"No composite actions directory found at: {composite_actions_path}")

# Initialize the global Task Queue
# This coordinates sequential task execution (one at a time)
task_queue = None  # Will be initialized after getting comet_path


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
@require_auth
def execute_url():
    """
    Execute a URL navigation task in Comet browser.
    
    Request Body:
        {
            "url": "https://example.com"
        }
    
    Response:
        {
            "status": "queued" or "started",
            "task_id": "uuid",
            "task_type": "url",
            "queue_position": 0 or N
        }
    
    Workflow:
        1. Validate URL parameter
        2. Check Comet browser availability
        3. Create URLTask object
        4. Submit to TaskQueue
        5. Return task info to client
    """
    # Step 1: Validate input
    data = request.json
    url = data.get('url')
    
    if not url:
        logger.warning("URL task requested without URL parameter")
        return jsonify({"error": "URL is required"}), 400

    # Step 2: Check task queue initialization
    if task_queue is None:
        return jsonify({"error": "Task queue not initialized"}), 500

    # Step 3: Create task object
    task = task_manager.create_url_task(url)
    logger.info(f"Created URL task {task.task_id} for: {url}")

    try:
        # Step 4: Submit to queue (non-blocking)
        task_queue.submit(task)
        
        # Get queue status to determine position
        queue_status = task_queue.get_status()
        is_current = queue_status['current'] and queue_status['current']['task_id'] == task.task_id
        queue_position = 0 if is_current else len([t for t in queue_status['queued'] if t['task_id'] == task.task_id])
        
        logger.info(f"URL task {task.task_id} submitted to queue (position: {queue_position})")
        
        # Step 5: Return success response
        return jsonify({
            "status": "started" if is_current else "queued",
            "task_id": task.task_id,
            "task_type": "url",
            "queue_position": queue_position,
            "message": "URL task queued successfully" if not is_current else "URL task started"
        }), 200
        
    except Exception as e:
        # Handle submission failures
        logger.error(f"Failed to submit URL task: {e}")
        task.fail(str(e))
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINTS - AI TASK EXECUTION (NEW)
# ============================================================================

@app.route('/execute/ai', methods=['POST'])
@require_auth
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
            "status": "queued" or "started",
            "task_id": "uuid",
            "task_type": "ai",
            "instruction": "Please summarize...",
            "queue_position": 0 or N
        }
    
    Workflow:
        1. Validate instruction parameter
        2. Create AITask object
        3. Submit to TaskQueue
        4. Return task info to client
    
    Note:
        The automation sequence runs in a background thread:
        - Click AI Assistant button
        - Click task input box
        - Type instruction
        - Click Send button
    """
    # Step 1: Validate input
    data = request.json
    instruction = data.get('instruction')
    coordinates = data.get('coordinates')  # Optional
    
    if not instruction:
        logger.warning("AI task requested without instruction")
        return jsonify({"error": "instruction is required"}), 400

    # Step 2: Check task queue initialization
    if task_queue is None:
        return jsonify({"error": "Task queue not initialized"}), 500

    # Step 3: Create AI task object
    task = task_manager.create_ai_task(instruction, coordinates)
    logger.info(f"Created AI task {task.task_id}: {instruction[:50]}...")

    try:
        # Step 4: Submit to queue (non-blocking)
        task_queue.submit(task)
        
        # Get queue status to determine position
        queue_status = task_queue.get_status()
        is_current = queue_status['current'] and queue_status['current']['task_id'] == task.task_id
        queue_position = 0 if is_current else len([t for t in queue_status['queued'] if t['task_id'] == task.task_id])
        
        logger.info(f"AI task {task.task_id} submitted to queue (position: {queue_position})")
        
        # Step 5: Return success response
        return jsonify({
            "status": "started" if is_current else "queued",
            "task_id": task.task_id,
            "task_type": "ai",
            "instruction": instruction,
            "queue_position": queue_position,
            "message": "AI task queued successfully" if not is_current else "AI task started"
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to submit AI task: {e}")
        task.fail(str(e))
        return jsonify({"error": str(e)}), 500



# ============================================================================
# API ENDPOINTS - GENERIC WORKFLOW EXECUTION (NEW)
# ============================================================================

@app.route('/execute/<task_type>', methods=['POST'])
@require_auth
def execute_workflow(task_type):
    """
    Execute a dynamic workflow by its task type name.
    
    This Generic Endpoint supports any YAML-defined workflow.
    Example: /execute/ai_assistant matches workflows/ai_assistant.yaml
    
    Request Body:
        {
            "instruction": "...",
            "other_param": "..."
        }
    """
    # 1. Skip if it's one of the hardcoded types (backward compatibility)
    if task_type in ['url', 'ai']:
        return jsonify({"error": f"Use dedicated endpoint /execute/{task_type}"}), 400
    
    # 2. Lookup workflow
    workflow = workflow_registry.get_by_name(task_type) or workflow_registry.get_by_endpoint(task_type)
    
    if not workflow:
        return jsonify({"error": f"Unknown task type: {task_type}"}), 404
        
    # 3. Validate inputs
    data = request.json or {}
    for input_spec in workflow.inputs:
        name = input_spec['name']
        required = input_spec.get('required', False)
        if required and name not in data:
            return jsonify({"error": f"Missing required input: {name}"}), 400
            
    # 4. Check capabilities
    if task_queue is None:
        return jsonify({"error": "Task queue not initialized"}), 500
        
    try:
        # 5. Create Configurable Task
        task = task_manager.create_configurable_task(workflow, data)
        logger.info(f"Created generic task {task.task_id} for workflow: {workflow.name}")
        
        # 6. Submit to Queue
        task_queue.submit(task)
        
        # 7. Get queue position
        queue_status = task_queue.get_status()
        is_current = queue_status['current'] and queue_status['current']['task_id'] == task.task_id
        queue_position = 0 if is_current else len([t for t in queue_status['queued'] if t['task_id'] == task.task_id])
        
        return jsonify({
            "status": "started" if is_current else "queued",
            "task_id": task.task_id,
            "task_type": task_type,
            "workflow_name": workflow.name,
            "queue_position": queue_position
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to submit workflow task: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API ENDPOINTS - STATUS & MONITORING
# ============================================================================

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """
    Get the current status of any task (URL, AI, or workflow-based).

    This endpoint is polled by the frontend every ~1 second.

    Process:
        1. Look up task by ID
        2. Check task-specific completion logic
        3. Auto-complete if task is done
        4. Return current status with step history (for workflow tasks)

    Returns:
        {
            "status": "running" | "done" | "failed",
            "task_id": "uuid",
            "task_type": "url" | "ai" | "custom",
            "url": "..." or "instruction": "...",
            "process_id": 12345,
            "step_history": [...]  // For workflow-based tasks
        }
    """
    # Step 1: Find task (supports short IDs now)
    task = task_manager.get_task(task_id)
    if not task:
        # Check if it might be an ambiguous short ID
        if len(task_id) <= 12:
            matches = [
                tid for tid in task_manager.tasks.keys()
                if tid.startswith(task_id)
            ]
            if len(matches) > 1:
                logger.warning(f"Ambiguous short task ID '{task_id}', matches: {matches}")
                return jsonify({
                    "error": f"Ambiguous task ID '{task_id}'",
                    "matches": matches[:5],  # Show first 5 matches
                    "hint": "Please use a longer prefix or full task ID"
                }), 400
        
        logger.warning(f"Status requested for unknown task: {task_id}")
        return jsonify({
            "error": "Task ID not found",
            "task_id": task_id,
            "hint": "Task may have been cleaned up or ID is incorrect"
        }), 404

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
        # Add automation progress for AI tasks
        response['automation_progress'] = task.get_automation_progress()
    elif task.task_type == TaskType.CUSTOM:
        # ConfigurableTask (workflow-based)
        if hasattr(task, 'workflow_config'):
            response['workflow_name'] = task.workflow_config.name
        if hasattr(task, 'inputs'):
            response['inputs'] = task.inputs
            # Add instruction for backward compatibility
            if 'instruction' in task.inputs:
                response['instruction'] = task.inputs['instruction']
        # Add progress info
        if hasattr(task, 'get_progress'):
            response['progress'] = task.get_progress()
        # Add step execution history
        if hasattr(task, 'get_step_history'):
            response['step_history'] = task.get_step_history()

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


@app.route('/manager/status', methods=['GET'])
def get_manager_status():
    """
    Get complete task queue status.
    
    This is the main endpoint for UI polling.
    Returns current executing task, queued tasks, and recently completed.
    
    Returns:
        {
            'current': {...} or None,
            'queued': [...],
            'completed': [...],
            'stats': {...}
        }
    """
    if task_queue is None:
        return jsonify({'error': 'Task queue not initialized'}), 500
    
    return jsonify(task_queue.get_status()), 200


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
        iteration = 0
        while True:
            try:
                iteration += 1
                logger.debug(f"Monitor iteration {iteration}: Checking tasks...")
                task_manager.monitor_tasks()

                # Log status every 10 iterations (50 seconds)
                if iteration % 10 == 0:
                    all_tasks = task_manager.get_all_tasks()
                    running_count = len([t for t in all_tasks.values() if t.get('status') == 'running'])
                    logger.info(f"Monitor status: {running_count} running task(s), {len(all_tasks)} total task(s)")
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                import traceback
                traceback.print_exc()
            time.sleep(5)  # Check every 5 seconds

    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()


# ============================================================================
# MAIN APPLICATION ENTRY
# ============================================================================

def run_server(local_only: bool = False):
    """
    Start the Flask backend server.
    
    This function is designed to be called from:
    1. Direct execution: python backend.py
    2. Tray application: import backend; backend.run_server()
    
    Args:
        local_only: If True, bind to 127.0.0.1 only (no API key required)
    """
    import atexit
    from utils.cleanup import cleanup_temp_files
    global task_queue

    # Register cleanup on normal exit
    atexit.register(cleanup_temp_files)

    logger.info("=" * 60)
    logger.info("Starting Comet Task Runner Backend")
    logger.info("=" * 60)

    # Check overlay module availability
    logger.info("Checking overlay module availability...")
    try:
        from overlay import StatusOverlay, OverlayConfig
        logger.info("✓ Overlay module loaded successfully")
    except ImportError as e:
        logger.warning(f"⚠ Overlay module not available: {e}")

    # Check keyboard module availability
    try:
        import keyboard
        logger.info("✓ Keyboard module available for ESC cancellation")
    except ImportError:
        logger.warning("⚠ Keyboard module not available - ESC cancellation disabled")
    
    # Security Check
    api_key = os.environ.get('COMET_API_KEY')
    
    if local_only:
        # Tray mode: allow local-only without API key
        host = '127.0.0.1'
        logger.info("Running in LOCAL-ONLY mode (no API key required)")
    elif not api_key:
        # Interactive mode: require API key
        logger.error("COMET_API_KEY not set!")
        if __name__ == '__main__':
            print("\n" + "!" * 80)
            print("CRITICAL: COMET_API_KEY environment variable is not set!")
            print("!" * 80)
            input("Press Enter to exit...")
            sys.exit(1)
        else:
            # Called from tray, fallback to local-only
            host = '127.0.0.1'
            logger.warning("Falling back to localhost-only mode")
    else:
        host = '0.0.0.0'
        logger.info(f"✓ API Key detected (Length: {len(api_key)})")
    
    # Initialize TaskQueue
    comet_path = get_comet_path()
    if comet_path:
        task_queue = TaskQueue(comet_path)
        logger.info(f"✓ TaskQueue initialized")
    else:
        logger.warning("⚠ Comet browser not found")
    
    logger.info("API Endpoints ready:")
    logger.info("  POST /execute/url")
    logger.info("  POST /execute/ai")
    logger.info("  GET  /status/<task_id>")
    logger.info("  GET  /manager/status")
    logger.info("=" * 60)
    
    # Start background monitoring thread
    start_task_monitor()
    
    try:
        logger.info(f"Server listening on {host}:5000")
        app.run(host=host, port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Backend shutting down...")
        if task_queue:
            task_queue.shutdown()
        cleanup_temp_files()
        logger.info("Goodbye!")


if __name__ == '__main__':
    run_server()


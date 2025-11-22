# Comet Task Runner

A Python-based tool to automate URL execution in the Comet Browser.

## Prerequisites

- **Python 3.x** installed and added to PATH.
- **Comet Browser** installed.

## Installation

1.  Open a terminal in this folder.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

### Option 1: One-Click Launcher (Recommended)
Double-click the **`run_app.bat`** file. 
- This will install dependencies (if missing) and launch the application.

### Option 2: Manual
1.  Run the frontend:
    ```bash
    python frontend.py
    ```
2.  The Frontend will automatically check if the Backend is running. If not, it will launch the Backend in a separate terminal window.

## Architecture

- **Frontend (`src/frontend.py`)**: A Tkinter GUI to manage URLs and trigger execution.
- **Backend (`src/backend.py`)**: A Flask server that handles the actual browser automation.
- **Task Manager (`src/task_manager.py`)**: Manages the lifecycle of each execution job.
- **`urls.json`**: Stores your URL list.

### Task Execution Lifecycle

Each URL execution creates an `ExecutionJob` that tracks:
1. **Task ID**: Unique identifier (UUID)
2. **Process ID**: Windows process ID of the browser
3. **Status**: created → running → done/failed
4. **Timestamps**: When created, started, and completed
5. **Process Info**: CPU, memory, status via `psutil`

**How Status Changes to "Done":**
- **Method 1 (Auto)**: When the backend detects the browser process has exited (checked during polling)
- **Method 2 (Manual)**: Browser script calls `POST /callback` with status="done"
- **Future**: AI/OpenCV screenshot analysis to detect task completion

## Understanding the "Health Check" (Polling)

You might notice the Frontend constantly sending requests to the Backend. This is **Polling**, not just a health check.

1.  **Why?**: The Backend (Server) cannot easily "push" a message to the Frontend (Client) to say "I'm done" without complex WebSockets.
2.  **How it works**:
    - When you start a task, the Frontend gets a `task_id`.
    - Every 1 second, the Frontend asks the Backend: *"Is Task X done yet?"* (`GET /status/<task_id>`).
    - The Backend checks if the process is still alive. If not, it auto-completes the task.
    - The Backend replies: *"No, still running"* or *"Yes, done"*.
    - When it hears "Yes", the Frontend turns the light **Green**.

## Usage

1.  **Add URL**: Type a URL and click "Add URL".
2.  **Execute**: Click "Execute" next to a URL.
    - **Yellow**: Request sent to browser.
    - **Green**: Browser launched successfully.
3.  **Remove**: Click "Remove" to delete a URL.

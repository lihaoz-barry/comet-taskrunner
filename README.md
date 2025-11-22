# Comet Task Runner

A Python-based automation tool for Comet Browser with support for URL navigation and AI assistant interaction tasks.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.x-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **URL Task Automation**: Automatically open and navigate to URLs in Comet Browser
- **AI Assistant Integration**: Automate AI assistant interactions with custom instructions
- **Component-Based Architecture**: Extensible task system with abstract base classes
- **Real-time Monitoring**: Track task status with process monitoring and polling
- **User-Friendly GUI**: Tkinter-based frontend for easy task management
- **REST API**: Flask backend for programmatic task execution

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

### Component Overview

```
comet-taskrunner/
├── src/
│   ├── frontend.py         # Tkinter GUI client
│   ├── backend.py          # Flask REST API server
│   ├── task_manager.py     # Task lifecycle manager
│   └── tasks/              # Task component package
│       ├── base_task.py    # Abstract base class
│       ├── url_task.py     # URL navigation task
│       └── ai_task.py      # AI assistant task
├── docs/                   # Detailed documentation
├── requirements.txt        # Python dependencies
└── urls.json              # URL persistence storage
```

### Architecture Layers

- **Frontend (`src/frontend.py`)**: Tkinter GUI for task management and monitoring
- **Backend (`src/backend.py`)**: Flask REST API server for task execution
- **Task Manager (`src/task_manager.py`)**: In-memory task storage and lifecycle management
- **Task Components (`src/tasks/`)**: Reusable, framework-independent task implementations

### API Endpoints

#### Task Execution
- `POST /execute/url` - Execute a URL navigation task
- `POST /execute/ai` - Execute an AI assistant task

#### Monitoring
- `GET /status/<task_id>` - Get task status
- `GET /jobs` - List all tasks
- `GET /health` - Server health check
- `POST /callback` - Manual task completion

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

### GUI Usage

1.  **Add URL**: Type a URL and click "Add URL"
2.  **Execute**: Click "Execute" next to a URL
    - **Yellow**: Task is running
    - **Green**: Task completed successfully
3.  **Remove**: Click "Remove" to delete a URL

### API Usage

#### Execute URL Task
```bash
curl -X POST http://127.0.0.1:5000/execute/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

#### Execute AI Task
```bash
curl -X POST http://127.0.0.1:5000/execute/ai \
  -H "Content-Type: application/json" \
  -d '{"instruction": "Please summarize this document"}'
```

#### Check Task Status
```bash
curl http://127.0.0.1:5000/status/<task_id>
```

## Technical Details

### Task Types

#### URLTask
- Launches Comet Browser with specified URL
- Auto-completes when browser process exits
- Simple process monitoring

#### AITask (Experimental)
- Launches Comet Browser
- Executes automation sequence (placeholder)
- AI-based completion detection (future)

### Task Lifecycle

```
CREATED → RUNNING → DONE/FAILED
```

Each task tracks:
- Unique task ID (UUID)
- Process ID and status
- Creation, start, and completion timestamps
- Process metrics (CPU, memory)

## Documentation

For detailed documentation, see the `docs/` directory:
- `架构说明（中文）.md` - Complete architecture guide (Chinese)
- `task_lifecycle.md` - Task lifecycle details
- `implementation_plan.md` - Development roadmap
- `组件化设计.md` - Component design patterns

## Future Development

- [ ] Complete AI task automation (mouse/keyboard control)
- [ ] Screenshot-based completion detection
- [ ] OpenCV/AI model integration
- [ ] Coordinate calibration tool
- [ ] Task scheduling and queuing
- [ ] Task history and analytics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- Python 3.x
- Flask (REST API)
- Tkinter (GUI)
- psutil (Process monitoring)

---

**Version**: 0.1.0
**Author**: Barry
**Repository**: [comet-taskrunner](https://github.com/lihaoz-barry/comet-taskrunner)

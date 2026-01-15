# Comet Task Runner

A Python-based automation tool for Comet Browser with support for URL navigation and AI assistant interaction tasks.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.x-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **URL Task Automation**: Automatically open and navigate to URLs in Comet Browser
- **AI Assistant Integration**: Automate AI assistant interactions with custom instructions
- **Visual Widget Detection**: Real-time bounding box animation with gradient fade-in/out when widgets are detected
- **Component-Based Architecture**: Extensible task system with abstract base classes
- **Real-time Monitoring**: Track task status with process monitoring and polling
- **User-Friendly GUI**: Tkinter-based frontend for easy task management
- **REST API**: Flask backend for programmatic task execution

## Prerequisites

- **Python 3.x** installed and added to PATH.
- **Comet Browser** installed.

## Installation

### Option 1: Download Pre-built Executable (Recommended)

**No Python installation required!**

1. Go to the [Releases page](https://github.com/lihaoz-barry/comet-taskrunner/releases)
2. Download the latest `backend-x.x.x.exe` file
3. Run the executable directly - the backend server will start automatically

### Option 2: Install from Source

1.  Open a terminal in this folder.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

### Option 1: Development Mode (Recommended for Debugging)
Double-click **`start.bat`** file.
- **Frontend**: Separate terminal window (logs visible)
- **Backend**: Separate terminal window (logs visible)
- Automatically detects and uses the best available terminal (Windows Terminal → PowerShell → CMD)
- Checks and installs dependencies
- **Best for**: Development, debugging, troubleshooting

## 🔒 Security Configuration (Important)

The backend now listens on `0.0.0.0` (all network interfaces) to allow Azure deployment. To secure this, you **MUST** set an API Key.

### Setting the API Key
You must set the `COMET_API_KEY` environment variable before running the backend.

**Option 1: Temporary (Current Session)**
```bash
set COMET_API_KEY=my-secret-password-123
```

**Option 2: Permanent (User Environment)**
```bash
setx COMET_API_KEY "my-secret-password-123"
# Note: Restart terminal after setx
```

**Option 3: .env file (Recommended)**
Create a `.env` file in the project root:
```ini
COMET_API_KEY=my-secret-password-123
```

### Authentication Logic
- **Localhost (127.0.0.1)**: No key required (Convenient for local dev)
- **Remote (Azure/Network)**: Must include header `X-API-Key: <your-key>`

## 🚀 How to Run (Background Mode)
Double-click **`start_background.bat`** file.
- **Frontend**: Hidden (no console, runs with pythonw)
- **Backend**: Separate terminal window (logs visible)
- Cleaner desktop with fewer windows
- **Best for**: Normal usage, production

### Option 3: Manual
1. Start backend:
   ```bash
   python src/backend.py
   # Or if you have the packaged version:
   dist/backend.exe
   ```
2. Start frontend (in a separate terminal):
   ```bash
   python src/frontend.py
   ```

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

1. **Add URL**: Type a URL and click "Add URL"
2. **Execute URL**: Click "Execute" next to a URL
   - **Yellow**: Task is running
   - **Green**: Task completed successfully
3. **AI Assistant**: Enter instruction in the AI prompt box
   - **Enter**: Submit task (shortcut)
   - **Shift+Enter**: New line for multi-line input
   - Click "🤖 Execute AI Task" button (alternative to Enter)
4. **Remove**: Click "Remove" to delete a URL

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
- `BOUNDING_BOX_VISUALIZATION.md` - Visual feedback feature documentation

## Visual Widget Detection

The system now includes **real-time visual feedback** when widgets are detected during automation:

- **Red Bounding Box**: Displays at the exact location of detected widgets
- **Smooth Gradient Animation**: Fast fade-in (0.3s) → display (0.5s) → fade-out (0.3s)
- **Non-intrusive**: Click-through overlay that doesn't interfere with automation
- **Automatic**: No configuration needed - works out of the box

To see the feature in action:
```bash
python demo_bounding_box.py
```

See `docs/BOUNDING_BOX_VISUALIZATION.md` for detailed documentation.

## Future Development

- [ ] Complete AI task automation (mouse/keyboard control)
- [ ] Screenshot-based completion detection
- [x] Visual feedback for widget detection (completed)
- [ ] OpenCV/AI model integration
- [ ] Coordinate calibration tool
- [ ] Task scheduling and queuing
- [ ] Task history and analytics

## 🚀 Release Automation

This repository uses GitHub Actions to automatically build and release the backend executable.

### How It Works

1. **Automatic Builds**: When code is merged to the `min` branch, GitHub Actions automatically:
   - Builds the backend using `build_backend.bat`
   - Reads version number from `version.txt`
   - Generates changelog from recent git commits
   - Creates a new GitHub Release
   - Uploads the compiled `backend.exe` to the release

2. **Version Management**: 
   - Update the version number in `version.txt` before merging to `min`
   - The release tag will be automatically created as `v{version}`

3. **Downloading Releases**:
   - Visit the [Releases page](https://github.com/lihaoz-barry/comet-taskrunner/releases)
   - Download the latest `backend-{version}.exe` or `backend.exe`
   - No installation needed - just run the executable

4. **Changelog**: Each release includes an automatically generated changelog showing all commits since the last release

### For Maintainers

To create a new release:
1. Update `version.txt` with the new version number (e.g., `0.2.0`)
2. Commit and push changes to the `min` branch
3. GitHub Actions will automatically build and create the release
4. Check the Actions tab to monitor the build progress
5. The new release will appear on the Releases page once complete

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
- OpenCV (Screenshot analysis)
- PyInstaller (Backend packaging - see [BUILD_GUIDE.md](BUILD_GUIDE.md))

---

**Version**: 0.1.0
**Author**: Barry
**Repository**: [comet-taskrunner](https://github.com/lihaoz-barry/comet-taskrunner)

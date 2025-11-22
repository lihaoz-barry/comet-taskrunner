# Implementation Plan - Comet Browser Task Runner

The goal is to create a decoupled system with a Backend Service (API) and a Frontend GUI. The backend will handle the logic of controlling the "Comet" browser and executing URLs, while the frontend will provide a user interface to trigger these actions and view status.

## User Review Required
> [!IMPORTANT]
> I will use **Flask** for the backend to provide a standard HTTP API.
> The Frontend will automatically launch the Backend in a separate terminal window on startup to ensure logs are visible.
> Port **5000** (default Flask port) will be used.

## Proposed Changes

### Project Root
#### [NEW] [backend.py](file:///c:/Users/Barry/Repos/comet-taskrunner/backend.py)
- **Framework**: Flask.
- **Endpoints**:
    - `POST /execute`: Accepts `{"url": "..."}`. Returns `{"task_id": "..."}`.
    - `POST /callback`: Accepts `{"task_id": "...", "status": "done"}`.
        - **Purpose**: This is how the **Browser** (or script) tells the **Backend** it is finished.
    - `GET /status/<task_id>`: Returns `{"status": "running" | "done"}`.
        - **Purpose**: This is how the **Frontend** checks if the task is done.
    - `GET /health`: Simple check to see if backend is ready.

### Completion Notification Architecture
To achieve "Backend knows it's done, then notifies Frontend":
1. **Browser -> Backend**: We use a **Webhook/Callback**.
    - The AI Agent in the browser must be configured to call `http://localhost:5000/callback` when finished.
2. **Backend -> Frontend**: We will use **Short Polling**.
    - **Why not WebSockets?**: WebSockets add significant complexity to a simple Tkinter + Flask setup (requires async servers, threading issues with Tkinter).
    - **Polling**: The Frontend will simply ask the Backend "Is Task X done?" every 1 second. This is robust, simple, and "real-time enough" for this use case.

- **Comet Logic**:

- **Comet Logic**:
    - **Dynamic Path Lookup**:
        - Query `HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\comet.exe` (and HKLM fallback) to find the executable path.
        - This matches the `Win+R` behavior described by the user.
    - Uses `subprocess` to manage the browser process.
- **Logging**: Standard Python logging to stdout (visible in the terminal window).

#### [MODIFIED] [frontend.py](file:///c:/Users/Barry/Repos/comet-taskrunner/frontend.py)
- **Persistence**:
    - Load `urls.json` on startup.
    - Save `urls.json` whenever a URL is added or removed.
    - Format: `[{"url": "...", "status": "idle"}, ...]` (Status resets to idle on load).
- **UI Layout**:
    - Use `grid` geometry manager for better alignment of Status | URL | Execute | Remove.
    - Fix spacing and padding.
- **New Features**:
    - **Remove Button**: Adds a "Remove" button to each row.
    - **History**: URLs persist across restarts.

#### [NEW] [urls.json](file:///c:/Users/Barry/Repos/comet-taskrunner/urls.json)
- Stores the list of URLs. Created automatically if missing.

#### [NEW] [requirements.txt](file:///c:/Users/Barry/Repos/comet-taskrunner/requirements.txt)
- `flask`
- `requests`

## Verification Plan

### Manual Verification
1. **Setup**: `pip install -r requirements.txt`
2. **Run Frontend**: `python frontend.py`
    - Verify a new terminal window opens running the Flask server.
3. **Visual Feedback**:
    - Status colors:
        - Default: None/White
        - Running: Yellow (Indicates request is being sent to backend/browser)
        - Done: Green (Indicates **Command Successfully Sent**).
            - *Note*: As per current requirements, this does NOT track the actual completion of the AI task within the browser. That is a future enhancement.
4. **Test Execution**:
    - Enter a URL in the GUI.
    - Click "Execute".
    - Verify:
        - Backend terminal shows log of received request.
        - Comet browser opens/focuses and loads URL.
        - GUI indicator turns Green.

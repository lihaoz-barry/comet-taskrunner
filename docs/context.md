# Comet Task Runner Context

## Project Overview
This project is a task runner for the "Comet" AI Browser. It consists of a decoupled Client-Server architecture.

## Architecture
- **Frontend**: A Python Tkinter GUI (`src/frontend.py`).
    - Manages a list of URLs.
    - Sends execution requests to the Backend.
    - Polls the Backend for task status.
- **Backend**: A Python Flask API (`src/backend.py`).
    - Exposes `POST /execute` to launch the browser.
    - Exposes `POST /callback` for the browser to report completion.
    - Exposes `GET /status/<task_id>` for the Frontend to poll.
    - Launches `comet.exe` using `subprocess`.

## Key Workflows
1.  **Execution**:
    - User clicks "Execute" -> Frontend calls `POST /execute`.
    - Backend launches Comet -> Returns `task_id`.
    - Frontend starts polling `GET /status/<task_id>`.
2.  **Completion**:
    - (Future) Browser script calls `POST /callback` with `{"status": "done"}`.
    - Backend updates state.
    - Frontend poll receives "done" -> Updates UI to Green.

## File Structure
- `src/`: Source code.
- `docs/`: Documentation and plans.
- `urls.json`: Persisted URL list.
- `run_app.bat`: One-click launcher.

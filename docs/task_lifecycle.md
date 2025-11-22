# Task Execution Lifecycle - Technical Details

## Overview
This document explains how the Comet Task Runner manages the execution lifecycle of each URL task.

## The Problem We Solved
**Before**: Status stayed "running" forever because there was no logic to detect completion.
**Now**: Status automatically changes to "done" when the browser process exits.

## Architecture

### Components

1. **ExecutionJob Class** (`src/task_manager.py`)
   - Represents a single task execution
   - Tracks: task_id, url, process_id, status, timestamps
   - Uses `psutil` to monitor the browser process

2. **TaskManager Class** (`src/task_manager.py`)
   - Manages all ExecutionJobs
   - Creates, retrieves, and updates jobs
   - Provides monitoring capabilities

3. **Backend Integration** (`src/backend.py`)
   - Creates ExecutionJob when `/execute` is called
   - Captures Windows process ID (PID) of launched browser
   - Checks process status during `/status` polling
   - Auto-completes job if process exited

## Execution Flow (Step-by-Step)

### 1. User Clicks "Execute"
```
Frontend → POST /execute {"url": "https://example.com"}
```

### 2. Backend Creates Job
```python
# backend.py line ~60
job = task_manager.create_job(url)
# Creates ExecutionJob with:
#   - task_id: "a1b2c3d4-..."
#   - status: CREATED
#   - created_at: timestamp
```

### 3. Backend Launches Browser
```python
# backend.py line ~68
process = subprocess.Popen([comet_path, url])
process_id = process.pid  # e.g., 12345
```

### 4. Backend Starts Job
```python
# backend.py line ~72
job.start(process_id)
# Updates:
#   - status: RUNNING
#   - process_id: 12345
#   - started_at: timestamp
#   - Attaches psutil.Process for monitoring
```

### 5. Backend Returns to Frontend
```json
{
  "status": "started",
  "task_id": "a1b2c3d4-...",
  "process_id": 12345
}
```

### 6. Frontend Polls Status
Every 1 second:
```
Frontend → GET /status/a1b2c3d4-...
```

### 7. Backend Checks Process
```python
# backend.py line ~109
if job.status == RUNNING and not job.is_running():
    job.complete()  # Auto-complete if process exited
```

The `job.is_running()` method (task_manager.py line ~107) checks:
```python
return self.process.is_running() and self.process.status() != psutil.STATUS_ZOMBIE
```

### 8. Status Changes to "Done"
**Two Methods:**

#### Method A (Auto - Process Exit Detection)
- User closes browser manually
- Process exits
- Backend detects during next poll
- Status → DONE

#### Method B (Manual - Callback)
- Browser script finishes task
- Calls `POST /callback {"task_id": "...", "status": "done"}`
- Status → DONE

### 9. Frontend Updates UI
- Receives status="done"
- Changes color from Yellow → Green

## Process Monitoring Details

### What We Track
Each ExecutionJob includes:
```python
{
    "task_id": "UUID",
    "url": "https://...",
    "process_id": 12345,           # Windows PID
    "status": "running",
    "created_at": "2025-11-22T...",
    "started_at": "2025-11-22T...",
    "process_info": {
        "pid": 12345,
        "name": "comet.exe",
        "status": "running",
        "cpu_percent": 2.5,
        "memory_mb": 450.2
    }
}
```

### Process Management Functions

**Location**: `src/task_manager.py`

| Function | Purpose | Returns |
|----------|---------|---------|
| `job.start(pid)` | Initialize job with process ID | None |
| `job.is_running()` | Check if process alive | bool |
| `job.get_process_info()` | Detailed process stats | dict |
| `job.complete()` | Mark as done | None |
| `job.fail(msg)` | Mark as failed | None |

## Future Enhancements

### 1. Screenshot-Based Detection
```python
# Planned for task_manager.py monitor_jobs()
def monitor_jobs(self):
    for job in running_jobs:
        if self.should_capture_screenshot(job):
            screenshot = self.capture_window(job.process_id)
            status = self.ai_detect_status(screenshot)
            if status == "completed":
                job.complete()
```

### 2. AI Pattern Detection
- Use OpenCV to capture browser window
- Use AI to detect success/failure patterns
- Auto-complete based on visual cues

### 3. Window Focus Management
- Track window handles (HWND)
- Ability to focus specific browser windows
- Useful for parallel execution

## API Reference

### GET /jobs
Get all jobs (debugging)
```bash
curl http://localhost:5000/jobs
```

Response:
```json
{
  "a1b2c3d4-...": {
    "task_id": "a1b2c3d4-...",
    "url": "https://...",
    "status": "done",
    "process_id": 12345,
    "is_process_alive": false,
    ...
  }
}
```

## Code Locations

| Feature | File | Line(s) |
|---------|------|---------|
| ExecutionJob class | src/task_manager.py | 28-145 |
| TaskManager class | src/task_manager.py | 148-232 |
| Job creation | src/backend.py | ~60 |
| Process launch | src/backend.py | ~68 |
| PID capture | src/backend.py | ~71 |
| Auto-complete check | src/backend.py | ~109 |
| Process monitoring | src/task_manager.py | ~107 |

## Troubleshooting

### Status Never Changes to Done
**Cause**: Process still running
**Solution**: Close browser manually or wait for task to complete

### Process Not Found
**Cause**: Browser crashed before PID captured
**Solution**: Check logs, ensure Comet is installed correctly

### Multiple Browser Windows
**Cause**: Each Execute creates new process
**Solution**: This is expected. Each URL gets its own browser instance.

"""
Comet Task Runner - Real-time Monitor UI (Table Style)
Connects to backend API to display live task status, logs, and queue info.
"""
import os
import sys
import time
import requests
from datetime import datetime

# ANSI codes
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
HOME = "\033[H"
CLEAR = "\033[2J"
BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"
WHITE = "\033[97m"
BG_BLUE = "\033[44m"

BACKEND_URL = "http://127.0.0.1:5000"
API_KEY = os.environ.get("COMET_API_KEY")

class BackendClient:
    def __init__(self):
        self.status = "connecting"
        self.task_data = None
        self.last_error = None
        
    def poll(self):
        try:
            headers = {"X-API-Key": API_KEY} if API_KEY else {}
            response = requests.get(f"{BACKEND_URL}/manager/status", headers=headers, timeout=0.5)
            
            if response.status_code == 200:
                self.task_data = response.json()
                self.status = "connected"
                self.last_error = None
            else:
                self.status = "error"
                self.last_error = f"HTTP {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            self.status = "disconnected"
            self.task_data = None
        except Exception as e:
            self.status = "error"
            self.last_error = str(e)

    def get_display_data(self):
        # Default empty state
        data = {
            "task_id": "-",
            "command": "-",
            "queue_size": 0,
            "status": self.status.upper(),
            "elapsed": 0,
            "progress": 0,
            "current_step_idx": 0,
            "total_steps": 0,
            "step_log": "Waiting for backend...",
            "steps": []
        }
        
        if self.status == "disconnected":
            data["step_log"] = f"{RED}Cannot connect to {BACKEND_URL}{RESET}"
            return data
            
        if not self.task_data:
            return data
            
        # Extract queue info
        stats = self.task_data.get("stats", {})
        data["queue_size"] = stats.get("queue_length", 0)
        
        # Extract current task info
        current = self.task_data.get("current")
        if current:
            data["task_id"] = current.get("task_id", "-")
            data["status"] = current.get("status", "UNKNOWN").upper()
            
            # Workflow name or inputs
            inputs = current.get("inputs", {})
            if "instruction" in inputs:
                data["command"] = inputs["instruction"][:40]
            elif "url" in current:
                data["command"] = current["url"]
            elif "workflow_name" in current:
                data["command"] = current["workflow_name"]
                
            # Progress details
            prog = current.get("progress", {})
            data["progress"] = prog.get("progress_percent", 0)
            data["current_step_idx"] = prog.get("current_step", 0)
            data["total_steps"] = prog.get("total_steps", 0)
            
            # Detailed step info
            details = prog.get("details", {})
            
            # Step Logs (The most specific log)
            logs = details.get("step_logs", [])
            if isinstance(logs, list) and logs:
                data["step_log"] = logs[-1]
            elif isinstance(logs, str) and logs:
                 data["step_log"] = logs
            else:
                data["step_log"] = prog.get("status_text", "")

            # Steps Visualization
            # Since backend doesn't send full step list (yet), we will simulate the list 
            # to match the layout the user liked, but focus on the active step.
            
            # Ideally, we should fetch the full workflow definition once to populate this list staticly.
            # For now, we'll create a dynamic "window" around the current step.
            
            current_idx = data["current_step_idx"]
            total = data["total_steps"]
            current_name = prog.get("status_text", f"Step {current_idx}")

            # Construct display list (mocking surrounding steps to maintain table look)
            display_steps = []
            
            # Previous steps (generic if unknown)
            for i in range(1, current_idx):
                display_steps.append({"id": f"{i:02d}", "name": f"Step {i}", "status": "DONE", "time": "-"})
                
            # Current step
            display_steps.append({"id": f"{current_idx:02d}", "name": current_name, "status": "RUNNING", "time": "..."})
            
            # Next steps (generic)
            for i in range(current_idx + 1, total + 1):
                display_steps.append({"id": f"{i:02d}", "name": f"Step {i}", "status": "WAITING", "time": ""})
            
            data["steps"] = display_steps
            
        else:
            data["status"] = "IDLE"
            data["step_log"] = "Ready for tasks"
            
        return data

def render_frame(client):
    data = client.get_display_data()
    lines = []
    
    # 1. Header Area
    lines.append(f"{BG_BLUE}{WHITE}{BOLD} COMET TASK MONITOR {RESET} {datetime.now().strftime('%H:%M:%S')}")
    lines.append(f"{CYAN}{'═'*80}{RESET}")
    
    # 2. Task Overview
    status_color = GREEN if data["status"] == "DONE" else (YELLOW if data["status"] == "RUNNING" else RED)
    if data["status"] == "IDLE": status_color = DIM

    lines.append(f" {BOLD}Task ID:{RESET} {data['task_id']}")
    lines.append(f" {BOLD}Command:{RESET} {data['command']}")
    lines.append(f" {BOLD}Status :{RESET} {status_color}{data['status']}{RESET}   {BOLD}Queue:{RESET} {data['queue_size']}")
    
    # 3. Progress Bar
    pct = data['progress']
    bar_w = 60
    filled = int(bar_w * pct / 100)
    bar = f"{GREEN}{'█' * filled}{DIM}{'░' * (bar_w - filled)}{RESET}"
    lines.append(f" Progress: [{bar}] {pct}%")
    lines.append("")

    # 4. Real-time Step Log Box (The critical part user wanted)
    lines.append(f" {BOLD}Current Step Log:{RESET}")
    lines.append(f" {YELLOW}┌{'─'*76}┐{RESET}")
    # Show last few log lines if possible, or just the latest one
    # For now, just the latest one prominent
    log_line = str(data['step_log'])[:74]
    lines.append(f" {YELLOW}│{RESET} {log_line:<74} {YELLOW}│{RESET}")
    lines.append(f" {YELLOW}└{'─'*76}┘{RESET}")
    lines.append("")

    # 5. Steps Table (The "Table Style" user missed)
    lines.append(f" {BOLD}{'Step':<6} {'Name':<50} {'Status':<10} {'Time':<8}{RESET}")
    lines.append(f" {DIM}{'─'*78}{RESET}")
    
    # Show a window of steps (e.g., current - 2 to current + 4)
    if data["steps"]:
        current_idx = data["current_step_idx"]
        start_idx = max(0, current_idx - 3)
        end_idx = min(len(data["steps"]), current_idx + 4)
        
        visible_steps = data["steps"][start_idx:end_idx]
        
        for s in visible_steps:
            s_status = s['status']
            color = GREEN if s_status == "DONE" else (YELLOW if s_status == "RUNNING" else DIM)
            if s_status == "RUNNING":
                prefix = f"{YELLOW}▶{RESET}"
            elif s_status == "DONE":
                prefix = f"{GREEN}✓{RESET}" 
            else:
                prefix = " "
                
            name = s['name'][:48]
            lines.append(f" {prefix} {s['id']:<4} {name:<50} {color}{s_status:<10}{RESET} {s['time']:<8}")
            
    elif data["status"] == "IDLE":
        lines.append(f" {DIM}   --   Waiting for task assignment...                        WAITING    --{RESET}")

    lines.append("")
    lines.append(f" {DIM}Press Ctrl+C to exit{RESET}")

    # Pad to fill screen
    while len(lines) < 25:
        lines.append("")
        
    print(HOME + '\n'.join(lines), end='', flush=True)

def main():
    print(HIDE_CURSOR + CLEAR, end='')
    client = BackendClient()
    
    try:
        while True:
            client.poll()
            render_frame(client)
            time.sleep(0.1) # Fast update
            
    except KeyboardInterrupt:
        print(SHOW_CURSOR)
        print(f"\n  Monitor closed.\n")

if __name__ == "__main__":
    main()

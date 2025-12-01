import tkinter as tk
from tkinter import messagebox, ttk
import requests
import subprocess
import time
import threading
import sys
import os
import shutil
import json

BACKEND_URL = "http://127.0.0.1:5000"
URLS_FILE = "urls.json"

class CometRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Comet Task Runner")
        self.root.geometry("1000x650")  # Increased width for status widget
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.urls = self.load_urls()
        
        # Create main container with left and right panels
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (existing content)
        self.left_panel = ttk.Frame(main_container)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel (task status widget)
        self.right_panel = ttk.LabelFrame(main_container, text="Task Queue Status", padding="10")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        self.right_panel.configure(width=300)
        
        self.create_widgets()
        self.create_status_widget()
        self.ensure_backend_running()
        
        # Start polling thread
        self.polling_active = True
        self.poll_thread = threading.Thread(target=self.poll_statuses, daemon=True)
        self.poll_thread.start()
        
        # Register cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Also register with atexit
        import atexit
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from utils.cleanup import cleanup_temp_files
        atexit.register(cleanup_temp_files)
    
    def on_closing(self):
        """Handle window close event"""
        print("Frontend closing...")
        try:
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            from utils.cleanup import cleanup_temp_files
            cleanup_temp_files()
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        self.polling_active = False  # Stop polling thread
        self.root.destroy()

    def load_urls(self):
        if os.path.exists(URLS_FILE):
            try:
                with open(URLS_FILE, 'r') as f:
                    data = json.load(f)
                    # Reset status to idle on load
                    for item in data:
                        item['status'] = 'idle'
                        item['task_id'] = None
                    return data
            except Exception as e:
                print(f"Error loading URLs: {e}")
        return [
            {"url": "https://www.google.com", "task_id": None, "status": "idle"},
            {"url": "https://www.perplexity.ai", "task_id": None, "status": "idle"}
        ]

    def save_urls(self):
        try:
            with open(URLS_FILE, 'w') as f:
                json.dump(self.urls, f, indent=2)
        except Exception as e:
            print(f"Error saving URLs: {e}")

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.left_panel, padding="10")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Comet Browser Task Runner", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        
        # ====================================================================
        # AI PROMPT SECTION (NEW!)
        # ====================================================================
        ai_frame = ttk.LabelFrame(self.left_panel, text="AI Assistant Task", padding="10")
        ai_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # AI Prompt label with shortcut hints
        prompt_label_text = "Prompt: (Enter to submit, Shift+Enter for new line)"
        ttk.Label(ai_frame, text=prompt_label_text, font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        
        # AI Prompt input (multi-line text box)
        self.ai_prompt_text = tk.Text(ai_frame, height=3, wrap=tk.WORD)
        self.ai_prompt_text.pack(fill=tk.X, pady=(5, 10))
        
        # Bind keyboard shortcuts
        def on_enter_key(event):
            # Check if Shift is held (event.state & 0x1 for Shift)
            if event.state & 0x1:  # Shift key is pressed
                return  # Allow default behavior (insert newline)
            else:
                # Submit the task
                self.execute_ai_task()
                return "break"  # Prevent default newline insertion
        
        self.ai_prompt_text.bind("<Return>", on_enter_key)
        
        # AI Execute button frame
        ai_btn_frame = ttk.Frame(ai_frame)
        ai_btn_frame.pack(fill=tk.X)
        
        self.ai_execute_btn = ttk.Button(
            ai_btn_frame, 
            text="🤖 Execute AI Task", 
            command=self.execute_ai_task,
            style="AI.TButton"
        )
        self.ai_execute_btn.pack(side=tk.RIGHT)
        
        # AI Status label
        self.ai_status_var = tk.StringVar(value="Status: Ready")
        ttk.Label(ai_btn_frame, textvariable=self.ai_status_var).pack(side=tk.LEFT)
        
        # Style for AI button
        self.style.configure("AI.TButton", foreground="#0066CC", font=("Helvetica", 10, "bold"))
        
        # ====================================================================
        # URL SECTION
        # ====================================================================
        url_section_frame = ttk.LabelFrame(self.left_panel, text="URL Tasks", padding="10")
        url_section_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Add URL Area
        add_frame = ttk.Frame(url_section_frame)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Use pack with expand/fill for the entry to take up available space
        ttk.Button(add_frame, text="Add URL", command=self.add_url).pack(side=tk.RIGHT, padx=(10, 0))
        self.new_url_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_url_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # List Area
        list_frame = ttk.Frame(url_section_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(list_frame)
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Ensure the scrollable frame expands to fill the canvas width
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.render_list()
    
    def create_status_widget(self):
        """Create the task queue status widget in the right panel."""
        # Scrollable canvas for task list
        status_canvas = tk.Canvas(self.right_panel, highlightthickness=0)
        status_scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=status_canvas.yview)
        
        self.status_frame = ttk.Frame(status_canvas)
        
        self.status_frame.bind(
            "<Configure>",
            lambda e: status_canvas.configure(scrollregion=status_canvas.bbox("all"))
        )
        
        status_canvas.create_window((0, 0), window=self.status_frame, anchor="nw")
        status_canvas.configure(yscrollcommand=status_scrollbar.set)
        
        status_canvas.pack(side="left", fill="both", expand=True)
        status_scrollbar.pack(side="right", fill="y")
        
        # Initial empty message
        ttk.Label(self.status_frame, text="No tasks yet", foreground="gray").pack(pady=20)

    def _on_canvas_configure(self, event):
        # Update the width of the scrollable_frame to match the canvas
        self.canvas.itemconfig(self.canvas.create_window((0,0), window=self.scrollable_frame, anchor="nw"), width=event.width)

    def render_list(self):
        # Clear current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Grid configuration
        self.scrollable_frame.columnconfigure(1, weight=1)

        for index, item in enumerate(self.urls):
            # Status Indicator
            status_color = "white"
            if item['status'] == "running":
                status_color = "yellow"
            elif item['status'] == "done":
                status_color = "#90EE90" # Light Green
            
            status_lbl = tk.Label(self.scrollable_frame, width=2, bg=status_color, relief="solid", borderwidth=1)
            status_lbl.grid(row=index, column=0, padx=5, pady=5, sticky="w")
            
            # URL Label
            ttk.Label(self.scrollable_frame, text=item['url'], anchor="w").grid(row=index, column=1, padx=5, pady=5, sticky="ew")
            
            # Execute Button
            btn_state = tk.NORMAL if item['status'] != "running" else tk.DISABLED
            ttk.Button(self.scrollable_frame, text="Execute", state=btn_state, 
                       command=lambda idx=index: self.execute_url(idx)).grid(row=index, column=2, padx=5, pady=5)

            # Remove Button
            ttk.Button(self.scrollable_frame, text="Remove", 
                       command=lambda idx=index: self.remove_url(idx)).grid(row=index, column=3, padx=5, pady=5)

    def add_url(self):
        url = self.new_url_var.get().strip()
        if url:
            self.urls.append({"url": url, "task_id": None, "status": "idle"})
            self.new_url_var.set("")
            self.save_urls()
            self.render_list()

    def remove_url(self, index):
        if 0 <= index < len(self.urls):
            del self.urls[index]
            self.save_urls()
            self.render_list()

    def execute_url(self, index):
        """Execute a URL task by calling the backend API."""
        url_item = self.urls[index]
        url = url_item['url']
        
        # Optimistic UI update to show task started
        self.urls[index]['status'] = "running"
        self.render_list()
        
        def run_request():
            try:
                # Call the URL task API endpoint
                response = requests.post(f"{BACKEND_URL}/execute/url", json={"url": url})
                if response.status_code == 200:
                    data = response.json()
                    # Update task_id for polling
                    self.urls[index]['task_id'] = data.get('task_id')
                    print(f"Started task {data.get('task_id')} for {url}")
                else:
                    print(f"Error executing {url}: {response.text}")
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to execute: {response.text}"))
                    self.urls[index]['status'] = "idle"
                    self.root.after(0, self.render_list)
            except Exception as e:
                print(f"Connection error: {e}")
                self.urls[index]['status'] = "idle"
                self.root.after(0, self.render_list)
                self.root.after(0, lambda: messagebox.showerror("Connection Error", "Could not connect to backend."))

        threading.Thread(target=run_request, daemon=True).start()
    
    def execute_ai_task(self):
        """Execute an AI task by calling the backend API (non-blocking)."""
        # Get prompt text
        prompt = self.ai_prompt_text.get("1.0", tk.END).strip()
        
        if not prompt:
            messagebox.showwarning("No Prompt", "Please enter a prompt for the AI assistant.")
            return
        
        # Update status (non-blocking - button stays enabled)
        self.ai_status_var.set("Status: Submitting...")
        
        def run_ai_request():
            try:
                # Call the AI task API endpoint
                response = requests.post(f"{BACKEND_URL}/execute/ai", json={"instruction": prompt})
                
                if response.status_code == 200:
                    data = response.json()
                    task_id = data.get('task_id')
                    queue_position = data.get('queue_position', 0)
                    status = data.get('status')
                    
                    print(f"Submitted AI task {task_id} (position: {queue_position})")
                    
                    # Update status based on queue position
                    if status == "started":
                        self.root.after(0, lambda: self.ai_status_var.set(f"Status: Running (Task: {task_id[:8]})"))
                    else:
                        self.root.after(0, lambda: self.ai_status_var.set(f"Status: Queued (Position: {queue_position + 1})"))
                    
                    # Clear input after successful submission
                    self.root.after(0, lambda: self.ai_prompt_text.delete("1.0", tk.END))
                else:
                    print(f"Error executing AI task: {response.text}")
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to execute: {response.text}"))
                    self.root.after(0, lambda: self.ai_status_var.set("Status: Error"))
            except Exception as e:
                print(f"Connection error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Connection Error", "Could not connect to backend."))
                self.root.after(0, lambda: self.ai_status_var.set("Status: Connection Error"))
        
        threading.Thread(target=run_ai_request, daemon=True).start()


    def poll_statuses(self):
        """Poll /manager/status endpoint for complete queue state."""
        print("🔄 Frontend polling thread started")
        
        while self.polling_active:
            time.sleep(1)  # Poll every 1 second
            
            try:
                # Poll the manager status endpoint (single API call for all tasks)
                response = requests.get(f"{BACKEND_URL}/manager/status", timeout=2)
                if response.status_code == 200:
                    manager_data = response.json()
                    
                    # Debug logging
                    print("=" * 60)
                    print("📡 FRONTEND RECEIVED DATA FROM BACKEND:")
                    print(f"  Current: {manager_data.get('current', {}).get('task_id', 'None')[:8] if manager_data.get('current') else 'None'}")
                    print(f"  Queued: {len(manager_data.get('queued', []))} tasks")
                    print(f"  Completed: {len(manager_data.get('completed', []))} tasks")
                    print("=" * 60)
                    
                    # Update status widget
                    self.root.after(0, lambda data=manager_data: self.update_status_widget(data))
                    
                    # Update AI status based on task state
                    self.root.after(0, lambda data=manager_data: self._update_ai_status(data))
                    
                    # Also update URL task statuses (backwards compatibility)
                    self._update_url_statuses(manager_data)
                else:
                    print(f"❌ Backend returned status code: {response.status_code}")
            except Exception as e:
                print(f"❌ Polling error: {e}")
                pass  # Ignore connection errors during polling
    
    def _update_url_statuses(self, manager_data):
        """Update URL task statuses from manager data (backwards compatibility)."""
        # Get all tasks from manager
        all_tasks = []
        if manager_data.get('current'):
            all_tasks.append(manager_data['current'])
        all_tasks.extend(manager_data.get('queued', []))
        all_tasks.extend(manager_data.get('completed', []))
        
        # Update URL items
        updated = False
        for item in self.urls:
            if item['task_id']:
                # Find matching task in manager data
                for task in all_tasks:
                    if task['task_id'] == item['task_id']:
                        new_status = task['status']
                        if new_status != item['status']:
                            item['status'] = new_status
                            updated = True
                        break
        
        if updated:
            self.root.after(0, self.render_list)
    
    def _update_ai_status(self, manager_data):
        """Update AI task status display based on manager data."""
        # Get current AI status text to see if we have a task ID tracked
        current_status = self.ai_status_var.get()
        
        # Extract task ID from current status if present
        if "Task:" in current_status:
            # Format is "Status: Running (Task: 12345678)"
            task_id_short = current_status.split("Task: ")[1].rstrip(")")
            
            # Find this task in manager data
            all_tasks = []
            if manager_data.get('current'):
                all_tasks.append(manager_data['current'])
            all_tasks.extend(manager_data.get('queued', []))
            all_tasks.extend(manager_data.get('completed', []))
            
            for task in all_tasks:
                if task.get('task_type') == 'ai' and task.get('task_id', '')[:8] == task_id_short:
                    # Update status based on task state
                    task_status = task.get('status')
                    if task_status == 'done':
                        self.ai_status_var.set(f"Status: ✓ Done (Task: {task_id_short})")
                    elif task_status == 'failed':
                        self.ai_status_var.set(f"Status: ✗ Failed (Task: {task_id_short})")
                    elif task_status == 'running':
                        # Check if it's current or queued
                        if manager_data.get('current') and manager_data['current'].get('task_id', '')[:8] == task_id_short:
                            self.ai_status_var.set(f"Status: Running (Task: {task_id_short})")
                        else:
                            # Still queued
                            queue_pos = next((i for i, t in enumerate(manager_data.get('queued', [])) 
                                            if t.get('task_id', '')[:8] == task_id_short), -1)
                            if queue_pos >= 0:
                                self.ai_status_var.set(f"Status: Queued (Position: {queue_pos + 1})")
                    break
    
    def update_status_widget(self, manager_data):
        """Update the task status widget with current queue state."""
        print(f"🖼️  RENDERING STATUS WIDGET")
        
        # Clear current widget
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        current_task = manager_data.get('current')
        queued_tasks = manager_data.get('queued', [])
        completed_tasks = manager_data.get('completed', [])
        
        print(f"  Rendering {1 if current_task else 0} current + {len(queued_tasks)} queued + {len(completed_tasks)} completed")
        
        # Show current task
        if current_task:
            print(f"  → Rendering current: {current_task.get('task_id')[:8]}")
            self._render_task_item(current_task, is_current=True)
        
        # Show queued tasks
        for task in queued_tasks:
            print(f"  → Rendering queued: {task.get('task_id')[:8]}")
            self._render_task_item(task, is_queued=True)
        
        # Show completed tasks
        for task in completed_tasks:
            print(f"  → Rendering completed: {task.get('task_id')[:8]}")
            self._render_task_item(task, is_completed=True)
        
        # If no tasks, show empty message
        if not current_task and not queued_tasks and not completed_tasks:
            print("  → No tasks, showing empty message")
            ttk.Label(self.status_frame, text="No tasks yet", foreground="gray").pack(pady=20)
    
    def _render_task_item(self, task, is_current=False, is_queued=False, is_completed=False):
        """Render a single task item in the status widget."""
        # Get task info
        task_type = task.get('task_type', 'unknown')
        
        # For AI tasks, show prompt (truncated)
        if task_type == "ai":
            prompt = task.get('instruction', 'Unknown')
            # Truncate long prompts
            if len(prompt) > 30:
                display_text = prompt[:27] + "..."
            else:
                display_text = prompt
        else:
            # For URL tasks, show URL
            url = task.get('url', 'Unknown')
            if len(url) > 30:
                display_text = url[:27] + "..."
            else:
                display_text = url
        
        # Determine status and colors
        if is_current:
            # Running task - Yellow/Orange background
            if task_type == "ai":
                automation_progress = task.get('automation_progress', {})
                current_step = automation_progress.get('current_step', 0)
                total_steps = automation_progress.get('total_steps', 7)
                status_text = f"Step {current_step}/{total_steps}"
            else:
                status_text = "Running"
            
            arrow = "→ "
            bg_color = "#FFD700"  # Gold/Yellow
            fg_color = "black"
            font_weight = "bold"
            
        elif is_queued:
            # Queued task - Light gray
            arrow = "  "
            status_text = "Queued"
            bg_color = "#F0F0F0"  # Light gray background
            fg_color = "#666666"  # Dark gray text
            font_weight = "normal"
            
        elif is_completed:
            # Completed task
            arrow = "  "
            if task.get('status') == 'done':
                status_text = "✓ Done"
                bg_color = "#90EE90"  # Light green  
                fg_color = "#006400"  # Dark green text
            else:
                status_text = "✗ Failed"
                bg_color = "#FFB6C1"  # Light red/pink
                fg_color = "#8B0000"  # Dark red text
            font_weight = "normal"
        else:
            arrow = "  "
            status_text = "Unknown"
            bg_color = "#FFFFFF"
            fg_color = "black"
            font_weight = "normal"
        
        # Create frame for this task
        item_frame = tk.Frame(self.status_frame, bg=bg_color, relief="ridge", bd=1)
        item_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Top line: Arrow + Prompt/URL
        top_label = tk.Label(
            item_frame,
            text=f"{arrow}{display_text}",
            anchor="w",
            font=("Segoe UI", 9, font_weight),
            bg=bg_color,
            fg=fg_color,
            padx=6,
            pady=3
        )
        top_label.pack(fill=tk.X)
        
        # Bottom line: Status
        status_label = tk.Label(
            item_frame,
            text=f"    {status_text}",  # Indent status
            anchor="w",
            font=("Segoe UI", 8),
            bg=bg_color,
            fg=fg_color,
            padx=6,
            pady=2
        )
        status_label.pack(fill=tk.X)
        
        # Third line: Task ID (small, gray text)
        task_id = task.get('task_id', 'unknown')
        task_id_short = task_id[:8] if len(task_id) >= 8 else task_id
        id_label = tk.Label(
            item_frame,
            text=f"    ID: {task_id_short}",
            anchor="w",
            font=("Segoe UI", 7),
            bg=bg_color,
            fg="#888888",  # Gray color
            padx=6,
            pady=1
        )
        id_label.pack(fill=tk.X)

    def ensure_backend_running(self):
        try:
            requests.get(f"{BACKEND_URL}/health", timeout=1)
            print("Backend is already running.")
        except requests.ConnectionError:
            print("Backend not running. Please start it manually.")
            print("Run: python src\\backend.py")

if __name__ == "__main__":
    root = tk.Tk()
    app = CometRunnerApp(root)
    root.mainloop()

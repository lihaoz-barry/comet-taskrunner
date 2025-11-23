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
        self.root.geometry("700x650")  # Increased height for AI section
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.urls = self.load_urls()
        
        self.create_widgets()
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
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Comet Browser Task Runner", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        
        # ====================================================================
        # AI PROMPT SECTION (NEW!)
        # ====================================================================
        ai_frame = ttk.LabelFrame(self.root, text="AI Assistant Task", padding="10")
        ai_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # AI Prompt label
        ttk.Label(ai_frame, text="Prompt:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
        
        # AI Prompt input (multi-line text box)
        self.ai_prompt_text = tk.Text(ai_frame, height=3, wrap=tk.WORD)
        self.ai_prompt_text.pack(fill=tk.X, pady=(5, 10))
        
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
        url_section_frame = ttk.LabelFrame(self.root, text="URL Tasks", padding="10")
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
        """Execute an AI task by calling the backend API."""
        # Get prompt text
        prompt = self.ai_prompt_text.get("1.0", tk.END).strip()
        
        if not prompt:
            messagebox.showwarning("No Prompt", "Please enter a prompt for the AI assistant.")
            return
        
        # Disable button during execution
        self.ai_execute_btn.configure(state=tk.DISABLED)
        self.ai_status_var.set("Status: Executing...")
        
        def run_ai_request():
            try:
                # Call the AI task API endpoint
                response = requests.post(f"{BACKEND_URL}/execute/ai", json={"instruction": prompt})
                
                if response.status_code == 200:
                    data = response.json()
                    task_id = data.get('task_id')
                    print(f"Started AI task {task_id}")
                    
                    # Update status
                    self.root.after(0, lambda: self.ai_status_var.set(f"Status: Running (Task: {task_id[:8]}...)"))
                    
                    # Poll for completion
                    self._poll_ai_task(task_id)
                else:
                    print(f"Error executing AI task: {response.text}")
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to execute: {response.text}"))
                    self.root.after(0, lambda: self.ai_status_var.set("Status: Error"))
                    self.root.after(0, lambda: self.ai_execute_btn.configure(state=tk.NORMAL))
            except Exception as e:
                print(f"Connection error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Connection Error", "Could not connect to backend."))
                self.root.after(0, lambda: self.ai_status_var.set("Status: Connection Error"))
                self.root.after(0, lambda: self.ai_execute_btn.configure(state=tk.NORMAL))
        
        threading.Thread(target=run_ai_request, daemon=True).start()
    
    def _poll_ai_task(self, task_id):
        """Poll AI task status until completion"""
        def poll():
            try:
                response = requests.get(f"{BACKEND_URL}/status/{task_id}")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')
                    
                    # Get automation progress if available
                    automation_progress = data.get('automation_progress', {})
                    completed_steps = automation_progress.get('completed_steps', 0)
                    total_steps = automation_progress.get('total_steps', 7)
                    
                    if status == "running":
                        self.root.after(0, lambda: self.ai_status_var.set(
                            f"Status: Running - Step {completed_steps}/{total_steps}"
                        ))
                        # Continue polling
                        threading.Timer(1.0, poll).start()
                    elif status == "done":
                        self.root.after(0, lambda: self.ai_status_var.set("Status: ✓ Completed"))
                        self.root.after(0, lambda: self.ai_execute_btn.configure(state=tk.NORMAL))
                        self.root.after(0, lambda: messagebox.showinfo("Success", "AI task completed successfully!"))
                    elif status == "failed":
                        error_msg = data.get('error_message', 'Unknown error')
                        self.root.after(0, lambda: self.ai_status_var.set(f"Status: ✗ Failed"))
                        self.root.after(0, lambda: self.ai_execute_btn.configure(state=tk.NORMAL))
                        self.root.after(0, lambda: messagebox.showerror("Task Failed", f"Error: {error_msg}"))
                    else:
                        # Continue polling for other statuses
                        threading.Timer(1.0, poll).start()
            except:
                # Retry on connection error
                threading.Timer(2.0, poll).start()
        
        poll()


    def poll_statuses(self):
        while self.polling_active:
            time.sleep(1) # Poll every 1 second
            updated = False
            for item in self.urls:
                if item['task_id'] and item['status'] == "running":
                    try:
                        response = requests.get(f"{BACKEND_URL}/status/{item['task_id']}")
                        if response.status_code == 200:
                            data = response.json()
                            new_status = data.get('status')
                            if new_status and new_status != item['status']:
                                item['status'] = new_status
                                updated = True
                    except:
                        pass # Ignore connection errors during polling
            
            if updated:
                self.root.after(0, self.render_list)

    def ensure_backend_running(self):
        try:
            requests.get(f"{BACKEND_URL}/health", timeout=1)
            print("Backend is already running.")
        except requests.ConnectionError:
            print("Backend not running. Launching...")
            
            if sys.platform == "win32":
                # Try to use Windows Terminal (wt) first, then PowerShell, then CMD
                backend_script = os.path.join(os.path.dirname(__file__), "backend.py")
                if shutil.which("wt"):
                    print("Launching in Windows Terminal...")
                    subprocess.Popen(["wt", "new-tab", "--title", "Comet Backend", "python", backend_script])
                elif shutil.which("powershell"):
                    print("Launching in PowerShell...")
                    subprocess.Popen(["start", "powershell", "-NoExit", "-Command", f"python {backend_script}"], shell=True)
                else:
                    print("Launching in CMD...")
                    subprocess.Popen(["start", "cmd", "/k", "python", backend_script], shell=True)
            else:
                subprocess.Popen(["python", "backend.py"])
            
            time.sleep(2)

if __name__ == "__main__":
    root = tk.Tk()
    app = CometRunnerApp(root)
    root.mainloop()

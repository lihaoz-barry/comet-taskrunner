"""
Process Delta Detector

Helps identify new processes created when launching an application.
Useful for determining which process(es) belong to Comet browser.
"""

import psutil
import time
import win32gui
import win32process
from datetime import datetime


class ProcessDeltaDetector:
    """Detect new processes by comparing snapshots"""

    def __init__(self):
        self.baseline = {}

    def record_baseline(self):
        """Record current process snapshot"""
        print("\n📸 Recording baseline processes...")

        self.baseline = {}
        for p in psutil.process_iter(['name', 'exe', 'create_time', 'pid']):
            try:
                self.baseline[p.pid] = {
                    'name': p.name(),
                    'exe': p.exe() if p.exe() else None,
                    'create_time': p.create_time(),
                    'cmdline': ' '.join(p.cmdline()) if p.cmdline() else None
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        print(f"✅ Baseline recorded: {len(self.baseline)} processes\n")

    def detect_new_processes(self, wait_seconds=3):
        """
        Detect new processes after waiting

        Args:
            wait_seconds: How long to wait before checking

        Returns:
            List of new process info dicts
        """
        print(f"⏳ Waiting {wait_seconds} seconds for new processes...")
        time.sleep(wait_seconds)

        current = {}
        for p in psutil.process_iter(['name', 'exe', 'create_time', 'pid', 'ppid']):
            try:
                current[p.pid] = {
                    'name': p.name(),
                    'exe': p.exe() if p.exe() else None,
                    'create_time': p.create_time(),
                    'pid': p.pid,
                    'ppid': p.ppid(),
                    'cmdline': ' '.join(p.cmdline()) if p.cmdline() else None
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Find new PIDs
        new_pids = set(current.keys()) - set(self.baseline.keys())

        if not new_pids:
            print("❌ No new processes detected\n")
            return []

        new_processes = [current[pid] for pid in new_pids]

        # Group by process name
        by_name = {}
        for proc in new_processes:
            name = proc['name']
            if name not in by_name:
                by_name[name] = []
            by_name[name].append(proc)

        print(f"\n🆕 Detected {len(new_processes)} new processes:\n")

        for name, procs in sorted(by_name.items()):
            print(f"  📦 {name} ({len(procs)} instance{'s' if len(procs) > 1 else ''})")
            for proc in procs:
                print(f"     PID: {proc['pid']}, Parent PID: {proc['ppid']}")
                if proc['exe']:
                    print(f"     Path: {proc['exe']}")
                if proc['cmdline'] and '--type=' in proc['cmdline']:
                    # Chromium process type
                    import re
                    match = re.search(r'--type=(\S+)', proc['cmdline'])
                    if match:
                        print(f"     Type: {match.group(1)} (Chromium sub-process)")

        print()
        return new_processes

    def find_windows_for_processes(self, process_names):
        """
        Find all windows belonging to specified processes

        Args:
            process_names: List of process names (e.g., ["Comet.exe"])

        Returns:
            List of window info dicts
        """
        windows = []

        # Normalize process names (lowercase for comparison)
        process_names_lower = [name.lower() for name in process_names]

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name()

                    if proc_name.lower() in process_names_lower:
                        title = win32gui.GetWindowText(hwnd)
                        class_name = win32gui.GetClassName(hwnd)

                        # Only record windows with titles
                        if title:
                            rect = win32gui.GetWindowRect(hwnd)
                            windows.append({
                                'hwnd': hwnd,
                                'title': title,
                                'class': class_name,
                                'process': proc_name,
                                'pid': pid,
                                'rect': rect
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return True

        win32gui.EnumWindows(callback, None)
        return windows

    def analyze_process_tree(self, root_process_names):
        """
        Analyze process tree for given root processes

        Args:
            root_process_names: List of process names to analyze
        """
        print("\n🌳 Process Tree Analysis:\n")

        root_processes = []
        for p in psutil.process_iter(['name', 'pid', 'ppid']):
            try:
                if p.name().lower() in [name.lower() for name in root_process_names]:
                    root_processes.append(p)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if not root_processes:
            print("  ⚠️ No matching processes found\n")
            return

        for root in root_processes:
            print(f"  🔹 {root.name()} (PID: {root.pid})")

            # Get children
            try:
                children = root.children(recursive=True)
                if children:
                    for child in children:
                        try:
                            print(f"     └─ {child.name()} (PID: {child.pid})")
                        except:
                            pass
                else:
                    print("     └─ (no child processes)")
            except:
                print("     └─ (cannot access)")

        print()


def main():
    """Main workflow"""
    print("=" * 80)
    print("PROCESS DELTA DETECTOR - Comet Browser Window Class Finder")
    print("=" * 80)

    detector = ProcessDeltaDetector()

    # Step 1: Record baseline
    print("\n📋 STEP 1: Recording Baseline Processes")
    print("-" * 80)
    detector.record_baseline()

    # Step 2: Wait for user to launch browser
    print("📋 STEP 2: Launch Comet Browser")
    print("-" * 80)
    input("\n▶️  Please open Comet browser now, then press ENTER to continue...\n")

    # Step 3: Detect new processes
    print("\n📋 STEP 3: Detecting New Processes")
    print("-" * 80)
    new_procs = detector.detect_new_processes(wait_seconds=3)

    if not new_procs:
        print("\n⚠️  No new processes found. Possible reasons:")
        print("   - Browser was already running before baseline")
        print("   - Browser took too long to start")
        print("   - Insufficient permissions to detect processes")
        print("\nPlease close all Comet instances and try again.\n")
        return

    # Step 4: Identify likely browser processes
    print("\n📋 STEP 4: Identifying Browser Processes")
    print("-" * 80)

    # Extract unique process names
    unique_names = list(set(p['name'] for p in new_procs))

    print(f"\nUnique process names detected: {', '.join(unique_names)}\n")

    # Common browser executable patterns
    browser_patterns = ['comet', 'browser', 'chrome', 'chromium']
    likely_browser = [
        name for name in unique_names
        if any(pattern in name.lower() for pattern in browser_patterns)
    ]

    if likely_browser:
        print(f"🎯 Likely browser process(es): {', '.join(likely_browser)}\n")
        target_processes = likely_browser
    else:
        print("⚠️ Cannot auto-identify browser process. Using all new processes.\n")
        target_processes = unique_names

    # Step 5: Analyze process tree
    detector.analyze_process_tree(target_processes)

    # Step 6: Find windows
    print("📋 STEP 5: Finding Windows for Browser Processes")
    print("-" * 80)

    windows = detector.find_windows_for_processes(target_processes)

    if not windows:
        print("\n❌ No windows found for detected processes.")
        print("   The browser might not have opened a visible window yet.")
        print("   Try running this tool again.\n")
        return

    print(f"\n✅ Found {len(windows)} window(s):\n")
    print("=" * 80)

    for i, win in enumerate(windows, 1):
        print(f"\nWindow #{i}")
        print(f"  Title:   {win['title']}")
        print(f"  Class:   {win['class']}  ← 💡 USE THIS FOR CONFIG!")
        print(f"  Process: {win['process']} (PID: {win['pid']})")
        print(f"  HWND:    {win['hwnd']}")
        rect = win['rect']
        print(f"  Size:    {rect[2]-rect[0]} x {rect[3]-rect[1]} pixels")
        print("-" * 80)

    # Step 7: Provide next steps
    print("\n📋 NEXT STEPS:")
    print("=" * 80)
    print("\n1️⃣  Copy the 'Class' value from the main browser window above")
    print("\n2️⃣  Create/update config/window_matching.yaml:")
    print("    ```yaml")
    print("    comet_browser:")
    print("      window_class: \"<paste class name here>\"")
    if likely_browser:
        print(f"      process_name: \"{likely_browser[0]}\"")
    print("      title_keywords:")
    print("        - \"Comet\"")
    print("        - \"Perplexity\"")
    print("      # ... (see docs/window_matching_strategies.md)")
    print("    ```")
    print("\n3️⃣  Test the configuration:")
    print("    python tools/debug_windows.py --filter Comet")
    print("\n4️⃣  Implement the optimized WindowManager (see documentation)")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()

"""
Window Debugging Tool

Helps identify window class names and process information for all visible windows.
Useful for configuring window matching strategies.
"""

import win32gui
import win32process
import win32con
import psutil
import sys
from pathlib import Path

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def print_all_windows(filter_keyword=None):
    """
    Print information about all visible windows.

    Args:
        filter_keyword: Optional string to filter windows by title
    """
    print("\n" + "=" * 80)
    print("VISIBLE WINDOWS ANALYSIS")
    print("=" * 80 + "\n")

    window_count = 0

    def callback(hwnd, _):
        nonlocal window_count

        # Only show visible windows
        if not win32gui.IsWindowVisible(hwnd):
            return True

        title = win32gui.GetWindowText(hwnd)

        # Skip windows without titles (usually hidden/system windows)
        if not title:
            return True

        # Apply filter if provided
        if filter_keyword and filter_keyword.lower() not in title.lower():
            return True

        # Get window information
        class_name = win32gui.GetClassName(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # Get process information
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc_path = proc.exe()
            parent = proc.parent()
            parent_name = parent.name() if parent else "None"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_name = "Unknown"
            proc_path = "Unknown"
            parent_name = "Unknown"

        # Get window rect and styles
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]

        try:
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        except:
            style = 0
            ex_style = 0

        # Get parent/owner
        parent_hwnd = win32gui.GetParent(hwnd)

        # Print formatted information
        window_count += 1
        print(f"Window #{window_count}")
        print(f"  Title:        {title}")
        print(f"  Class:        {class_name}  ← IMPORTANT for matching!")
        print(f"  HWND:         {hwnd}")
        print(f"  Process:      {proc_name} (PID: {pid})")
        print(f"  Path:         {proc_path}")
        print(f"  Parent Proc:  {parent_name}")
        print(f"  Size:         {width} x {height} pixels")
        print(f"  Position:     ({rect[0]}, {rect[1]}) to ({rect[2]}, {rect[3]})")
        print(f"  Parent HWND:  {parent_hwnd} {'(child window)' if parent_hwnd else '(top-level)'}")

        # Window characteristics
        characteristics = []
        if win32gui.IsIconic(hwnd):
            characteristics.append("Minimized")
        if ex_style & win32con.WS_EX_TOOLWINDOW:
            characteristics.append("Tool Window")
        if ex_style & win32con.WS_EX_APPWINDOW:
            characteristics.append("App Window")
        if ex_style & win32con.WS_EX_TOPMOST:
            characteristics.append("Always On Top")

        if characteristics:
            print(f"  Traits:       {', '.join(characteristics)}")

        print("-" * 80 + "\n")

        return True

    win32gui.EnumWindows(callback, None)

    print(f"\nTotal visible windows: {window_count}")
    print("=" * 80 + "\n")


def print_browser_windows():
    """Print only potential browser windows"""
    print("\n" + "=" * 80)
    print("POTENTIAL BROWSER WINDOWS")
    print("=" * 80 + "\n")

    # Common browser window classes
    browser_classes = {
        "Chrome_WidgetWin_1": "Chromium-based (Chrome, Edge, Comet?, etc.)",
        "MozillaWindowClass": "Firefox",
        "ApplicationFrameWindow": "Edge (UWP)",
        "OperaWindowClass": "Opera",
        "BraveWindowClass": "Brave"
    }

    found_count = 0

    def callback(hwnd, _):
        nonlocal found_count

        if not win32gui.IsWindowVisible(hwnd):
            return True

        class_name = win32gui.GetClassName(hwnd)

        # Check if it's a known browser class
        if class_name in browser_classes:
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return True

            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                proc_path = proc.exe()
            except:
                proc_name = "Unknown"
                proc_path = "Unknown"

            rect = win32gui.GetWindowRect(hwnd)

            found_count += 1
            print(f"Browser Window #{found_count}")
            print(f"  Title:    {title}")
            print(f"  Class:    {class_name}")
            print(f"  Type:     {browser_classes[class_name]}")
            print(f"  Process:  {proc_name} (PID: {pid})")
            print(f"  Path:     {proc_path}")
            print(f"  Size:     {rect[2]-rect[0]} x {rect[3]-rect[1]}")
            print("-" * 80 + "\n")

        return True

    win32gui.EnumWindows(callback, None)

    if found_count == 0:
        print("⚠️ No browser windows detected with known classes.")
        print("   Try running with --all to see all windows.\n")
    else:
        print(f"Found {found_count} browser windows.\n")

    print("=" * 80 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Debug Windows - Identify window classes and process info"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all visible windows (default: only browser windows)"
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Filter windows by title keyword (case-insensitive)"
    )

    args = parser.parse_args()

    print("\n🔍 Window Debugging Tool")
    print("=" * 80)

    if args.all:
        print_all_windows(filter_keyword=args.filter)
    else:
        if args.filter:
            print(f"\n🔎 Filtering windows by keyword: '{args.filter}'")
            print_all_windows(filter_keyword=args.filter)
        else:
            print_browser_windows()

    print("\n📝 Usage Tips:")
    print("  1. The 'Class' field is the most reliable identifier")
    print("  2. Copy the class name to config/window_matching.yaml")
    print("  3. Use --filter 'Comet' to find only Comet-related windows")
    print("  4. Use --all to see all windows on your system\n")


if __name__ == "__main__":
    main()

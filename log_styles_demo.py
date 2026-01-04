
import time
import sys
from datetime import datetime

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BG_BLUE = "\033[44m"

def print_separator(title):
    print(f"\n{BOLD}{'='*20} {title} {'='*20}{RESET}\n")

# ==========================================
# STYLE 1: Modern Minimalist (Emoji + Color)
# ==========================================
def style_1_minimal():
    print_separator("STYLE 1: Modern Minimalist")
    
    print(f"{DIM}10:00:01{RESET} {BLUE}ℹ{RESET}  Backend started on port 5000")
    print(f"{DIM}10:00:02{RESET} {GREEN}✔{RESET}  TaskQueue initialized")
    print(f"{DIM}10:00:05{RESET} {MAGENTA}🚀 TASK STARTED{RESET} {BOLD}Open Youtube and Search{RESET} (ID: 1a2b3c)")
    
    steps = [
        ("Open Browser", "running"),
        ("Open Browser", "done"),
        ("Navigate to URL", "running"),
        ("Navigate to URL", "done"),
        ("Find Search Bar", "running"),
        ("Find Search Bar", "failed")
    ]
    
    for step, status in steps:
        ts = datetime.now().strftime("%H:%M:%S")
        if status == "running":
            print(f"{DIM}{ts}{RESET} {YELLOW}▶{RESET}  Step: {step}...")
        elif status == "done":
            print(f"{DIM}{ts}{RESET} {GREEN}✔{RESET}  Step: {step} {GREEN}Completed{RESET}")
        elif status == "failed":
            print(f"{DIM}{ts}{RESET} {RED}✖{RESET}  Step: {step} {RED}FAILED{RESET}")
            print(f"          {RED}Error: Element not found at (100, 200){RESET}")

# ==========================================
# STYLE 2: Structured Blocks (Readable Separators)
# ==========================================
def style_2_blocks():
    print_separator("STYLE 2: Structured Blocks")
    
    print(f"[{CYAN}INFO{RESET}] Backend started on port 5000")
    print(f"[{CYAN}INFO{RESET}] TaskQueue initialized")
    print("-" * 60)
    print(f"{BG_BLUE}{WHITE}{BOLD} NEW TASK: Open Youtube and Search {RESET}")
    print(f"ID: 1a2b3c | User: Barry")
    print("-" * 60)
    
    steps = [
        ("Open Browser", "DONE"),
        ("Navigate to URL", "DONE"),
        ("Find Search Bar", "FAILED")
    ]
    
    for step, status in steps:
        time.sleep(0.1)
        if status == "DONE":
            color = GREEN
            icon = "[+]"
        else:
            color = RED
            icon = "[!]"
            
        print(f"{BOLD}STEP: {step}{RESET}")
        print(f"  {DIM}> Executing action...{RESET}")
        if status == "FAILED":
             print(f"  {color}{icon} Status: {status}{RESET} - Element not found")
        else:
             print(f"  {color}{icon} Status: {status}{RESET}")
        print(f"{DIM}{'-'*30}{RESET}")

# ==========================================
# STYLE 3: High Contrast (Headers & Keywords)
# ==========================================
def style_3_high_contrast():
    print_separator("STYLE 3: High Contrast")
    
    print(f"{GREEN}[SYSTEM]{RESET} Backend ready")
    
    # Task Start
    print(f"\n{YELLOW}┌──────────────────────────────────────────────────┐{RESET}")
    print(f"{YELLOW}│ STARTING TASK: Open Youtube                      │{RESET}")
    print(f"{YELLOW}└──────────────────────────────────────────────────┘{RESET}")
    
    print(f"\n{CYAN}STEP 1: Open Browser{RESET}")
    print(f"   Status: {GREEN}SUCCESS{RESET}")
    
    print(f"\n{CYAN}STEP 2: Navigate to URL{RESET}")
    print(f"   Target: youtube.com")
    print(f"   Status: {GREEN}SUCCESS{RESET}")

    print(f"\n{CYAN}STEP 3: Find Search Bar{RESET}")
    print(f"   Attempt: 1/3")
    print(f"   Status: {RED}FAILED{RESET} (Timeout)")
    
    print(f"\n{RED}┌──────────────────────────────────────────────────┐{RESET}")
    print(f"{RED}│ TASK FAILED: Element not found                   │{RESET}")
    print(f"{RED}└──────────────────────────────────────────────────┘{RESET}")

if __name__ == "__main__":
    style_1_minimal()
    print("\n\n")
    style_2_blocks()
    print("\n\n")
    style_3_high_contrast()

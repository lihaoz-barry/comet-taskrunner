import logging
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

class CustomFormatter(logging.Formatter):
    """
    Hybrid Formatter:
    - Style 1: Emojis and Colors for steps
    - Style 3: Boxes for Task Start/End/Failure
    """
    
    def format(self, record):
        # 1. Timestamp
        ts = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        timestamp = f"{DIM}{ts}{RESET}"
        
        msg = record.getMessage()
        
        # 2. High Contrast Boxes (Task Start/End/Fatal)
        if "TASK STARTED" in msg or "TASK FAILED" in msg:
            color = GREEN if "STARTED" in msg else RED
            border = f"{color}┌{'─'*60}┐{RESET}"
            content = f"{color}│ {msg:<58} │{RESET}"
            bottom = f"{color}└{'─'*60}┘{RESET}"
            return f"\n{border}\n{timestamp} {content}\n{bottom}"

        # 2b. Box for Step Start (Cyan)
        if "Executing step" in msg:
            color = CYAN
            border = f"{color}┌{'─'*60}┐{RESET}"
            content = f"{color}│ ▶ {msg:<56} │{RESET}"
            bottom = f"{color}└{'─'*60}┘{RESET}"
            return f"\n{border}\n{timestamp} {content}\n{bottom}"
            
        # 3. Step Logs (Style 1)
        if "Step:" in msg:
            if "Completed" in msg or "Success" in msg:
                return f"{timestamp} {GREEN}✔{RESET}  {msg}"
            elif "Failed" in msg or "Error" in msg:
                return f"{timestamp} {RED}✖{RESET}  {msg}"
            elif "..." in msg:
                return f"{timestamp} {YELLOW}▶{RESET}  {msg}"
                
        # 4. Standard Info (Minimalist)
        if record.levelno == logging.INFO:
            return f"{timestamp} {BLUE}ℹ{RESET}  {msg}"
        elif record.levelno == logging.WARNING:
            return f"{timestamp} {YELLOW}⚠  {msg}{RESET}"
        elif record.levelno == logging.ERROR:
            return f"{timestamp} {RED}✖  {msg}{RESET}"
            
        # Default
        return f"{timestamp} {msg}"

def setup_logging():
    """Configure root logger with custom formatter and filters"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(console_handler)
    
    # Filter Noise
    logging.getLogger("werkzeug").setLevel(logging.ERROR) # Hide HTTP 200s
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("automation.window_manager").setLevel(logging.WARNING) # Hide noisy window checks

    return root_logger

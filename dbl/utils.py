"""Utility functions for DBL"""

import subprocess
from .constants import Color
from .errors import DBLError


def log(msg, type="info"):
    """Log messages with color coding"""
    if type == "header": 
        print(f"{Color.HEADER}🚀 {msg}{Color.ENDC}")
    elif type == "success": 
        print(f"{Color.OKGREEN}✅ {msg}{Color.ENDC}")
    elif type == "warn": 
        print(f"{Color.WARNING}⚠️  {msg}{Color.ENDC}")
    elif type == "error": 
        print(f"{Color.FAIL}❌ {msg}{Color.ENDC}")
    elif type == "branch": 
        print(f"{Color.OKCYAN}🌿 {msg}{Color.ENDC}")
    elif type == "info": 
        print(f"ℹ️  {msg}{Color.ENDC}")
    else: 
        print(msg)


def log_progress(current, total, item_name="item", extra=""):
    """Log progress with interactive line update (like npm)"""
    import sys
    percent = int((current / total) * 100) if total > 0 else 0
    bar_length = 30
    filled = int((bar_length * current) / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_length - filled)
    
    # Truncate extra text to prevent overflow
    max_extra_len = 35
    if len(extra) > max_extra_len:
        extra = extra[:max_extra_len-3] + "..."
    
    # Build message with fixed width
    msg = f'\r⏳ [{bar}] {percent:3d}% ({current}/{total}) {item_name} {extra}'
    # Pad with spaces to clear previous longer text
    msg = msg.ljust(100)
    
    sys.stdout.write(msg)
    sys.stdout.flush()
    
    # Print newline when done
    if current >= total:
        sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line completely
        sys.stdout.flush()


def clear_progress():
    """Clear the progress line"""
    import sys
    sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line
    sys.stdout.flush()


def confirm_action(message):
    """Ask user for confirmation"""
    try:
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print()
        return False


def run_command(cmd, capture=False, env=None, show_stderr=False):
    """Execute a shell command"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            env=env
        )
        if show_stderr and capture and result.stderr:
            log(f"   stderr: {result.stderr.strip()}", "warn")
        return result.stdout.strip() if capture else None
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        if show_stderr or capture:
            log(f"   Command failed: {cmd[:100]}...", "error")
            log(f"   Error: {error_msg}", "error")
        raise DBLError(f"Failed internal command.\n   Cmd: {cmd}\n   Err: {error_msg}")

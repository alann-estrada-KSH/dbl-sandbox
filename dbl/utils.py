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


def confirm_action(message):
    """Ask user for confirmation"""
    try:
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print()
        return False


def run_command(cmd, capture=False, env=None):
    """Execute a shell command"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            env=env
        )
        return result.stdout.strip() if capture else None
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        raise DBLError(f"Failed internal command.\n   Cmd: {cmd}\n   Err: {error_msg}")

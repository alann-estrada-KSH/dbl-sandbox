"""Update command - Check and install DBL updates"""

import sys
import subprocess
import urllib.request
import json
from dbl.constants import VERSION
from dbl.utils import log


def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import yaml
        return True
    except ImportError:
        return False


def install_dependencies():
    """Install missing dependencies"""
    log("Installing missing dependencies...", "info")
    try:
        cmd = [sys.executable, "-m", "pip", "install", "PyYAML>=6.0"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            log("✓ Dependencies installed successfully!", "success")
            return True
        else:
            log("Failed to install dependencies.", "error")
            log(f"Error: {result.stderr}", "error")
            return False
    except Exception as e:
        log(f"Failed to install dependencies: {e}", "error")
        return False


def cmd_update(args):
    """Check for updates and optionally install them"""
    
    # First check if dependencies are installed
    if not check_dependencies():
        log("⚠️  Missing required dependencies (PyYAML)", "warning")
        if not args.yes:
            response = input("Do you want to install missing dependencies? (y/n): ").lower()
            if response not in ['y', 'yes']:
                log("Cannot proceed without dependencies.", "error")
                log("Install manually: pip install PyYAML>=6.0", "info")
                return
        
        if not install_dependencies():
            log("Failed to install dependencies. Please install manually:", "error")
            log("  pip install -r requirements.txt", "info")
            return
        
        log("Dependencies installed. You may need to restart your terminal.", "info")
        print()
    
    log("Checking for updates...", "info")
    
    try:
        # Get latest release from GitHub
        repo_url = "https://api.github.com/repos/alann-estrada-KSH/dbl-sandbox/releases/latest"
        
        req = urllib.request.Request(repo_url)
        req.add_header('User-Agent', 'DBL-Update-Checker')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get('tag_name', '').lstrip('v')
            release_url = data.get('html_url', '')
            release_notes = data.get('body', 'No release notes available.')
            
            # Compare versions
            current = VERSION.replace('-alpha', '').replace('-beta', '')
            latest = latest_version.replace('-alpha', '').replace('-beta', '')
            
            log(f"Current version: {VERSION}", "info")
            log(f"Latest version: {latest_version}", "info")
            
            if current == latest or current > latest:
                log("✓ You are already using the latest version!", "success")
                return
            
            # New version available
            log(f"\n{'='*60}", "info")
            log("🎉 A new version is available!", "success")
            log(f"{'='*60}\n", "info")
            
            # Show release notes (first 500 chars)
            if release_notes:
                notes_preview = release_notes[:500]
                if len(release_notes) > 500:
                    notes_preview += "..."
                log("Release notes:", "info")
                print(notes_preview)
                print()
            
            # Ask user if they want to update
            if not args.yes:
                response = input(f"Do you want to update to version {latest_version}? (y/n): ").lower()
                if response not in ['y', 'yes']:
                    log("Update cancelled.", "info")
                    return
            
            # Perform update
            log("\nInstalling update...", "info")
            
            # Method 1: Try pip install from git
            try:
                cmd = [
                    sys.executable, "-m", "pip", "install", "--upgrade",
                    "git+https://github.com/alann-estrada-KSH/dbl-sandbox.git"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    log("✓ Update successful!", "success")
                    log(f"DBL has been updated to version {latest_version}", "success")
                    log("\nPlease restart your terminal or run 'hash -r' to use the new version.", "info")
                else:
                    log("Failed to install update automatically.", "error")
                    log(f"\nPlease update manually:", "info")
                    log(f"  pip install --upgrade git+https://github.com/alann-estrada-KSH/dbl-sandbox.git", "info")
                    log(f"\nOr visit: {release_url}", "info")
                    
            except Exception as e:
                log(f"Failed to install update: {e}", "error")
                log(f"\nPlease update manually:", "info")
                log(f"  pip install --upgrade git+https://github.com/alann-estrada-KSH/dbl-sandbox.git", "info")
                log(f"\nOr visit: {release_url}", "info")
                
    except urllib.error.URLError as e:
        log(f"Could not connect to GitHub: {e}", "error")
        log("Please check your internet connection.", "info")
    except json.JSONDecodeError:
        log("Could not parse GitHub response.", "error")
    except Exception as e:
        log(f"Error checking for updates: {e}", "error")

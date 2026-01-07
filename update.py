#!/usr/bin/env python3
"""
Auto-update script for DBL
Checks for updates from GitHub releases and installs them
"""

import os
import sys
import json
import urllib.request
import subprocess
import platform
from pathlib import Path

GITHUB_REPO = "alann-estrada-KSH/dbl-sandbox"
CURRENT_VERSION = "0.0.1-alpha"

def get_latest_release():
    """Get latest release info from GitHub"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return {
                'version': data['tag_name'].lstrip('v'),
                'assets': data['assets']
            }
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return None

def download_asset(asset_url, filename):
    """Download asset from GitHub"""
    try:
        with urllib.request.urlopen(asset_url) as response:
            with open(filename, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def install_update(filename):
    """Install the downloaded update"""
    system = platform.system().lower()

    if filename.endswith('.whl'):
        # Install wheel
        return run_cmd(f"pip install --upgrade {filename}")
    elif filename.endswith('.exe') and system == "windows":
        # For exe, replace current exe
        exe_path = sys.executable
        # This is complex, better to use pip
        return run_cmd(f"pip install --upgrade dbl")
    elif filename.endswith('.deb') and system == "linux":
        return run_cmd(f"sudo dpkg -i {filename}")
    else:
        print(f"Unsupported file type: {filename}")
        return False

def run_cmd(cmd):
    """Run command"""
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_for_updates():
    """Check if update is available"""
    print("🔍 Checking for updates...")

    release = get_latest_release()
    if not release:
        return False

    latest_version = release['version']
    if latest_version == CURRENT_VERSION:
        print("✅ You have the latest version")
        return False

    print(f"📦 New version available: {latest_version}")
    return release

def update():
    """Perform update"""
    release = check_for_updates()
    if not release:
        return

    # Find appropriate asset
    system = platform.system().lower()
    assets = release['assets']

    asset = None
    if system == "windows":
        asset = next((a for a in assets if a['name'].endswith('.exe')), None)
    elif system == "linux":
        asset = next((a for a in assets if a['name'].endswith('.deb')), None)
    elif system == "darwin":
        asset = next((a for a in assets if a['name'].endswith('.dmg')), None)

    # Fallback to wheel
    if not asset:
        asset = next((a for a in assets if a['name'].endswith('.whl')), None)

    if not asset:
        print("❌ No suitable update found for your system")
        return

    print(f"⬇️  Downloading {asset['name']}...")

    if download_asset(asset['browser_download_url'], asset['name']):
        print("✅ Download complete")
        print("🔄 Installing update...")

        if install_update(asset['name']):
            print("✅ Update installed successfully!")
            print("Please restart DBL")
        else:
            print("❌ Update installation failed")
    else:
        print("❌ Download failed")

if __name__ == "__main__":
    update()
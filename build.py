#!/usr/bin/env python3
"""
Build script for DBL - Create distributable packages
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_cmd(cmd, cwd=None):
    """Run command and return success"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False

def build_wheel():
    """Build Python wheel"""
    print("🔨 Building Python wheel...")
    if run_cmd("python -m build --wheel"):
        print("✅ Wheel built successfully")
        return True
    return False

def build_exe():
    """Build Windows .exe with PyInstaller"""
    print("🔨 Building Windows .exe...")
    # Install pyinstaller if needed
    run_cmd("pip install pyinstaller")
    # Create spec file or use simple
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dbl/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dbl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    with open('dbl.spec', 'w') as f:
        f.write(spec_content)
    if run_cmd("pyinstaller --onefile dbl.spec"):
        print("✅ .exe built successfully")
        return True
    return False

def build_deb():
    """Build Debian .deb package"""
    print("🔨 Building Debian .deb...")
    # Install stdeb
    run_cmd("pip install stdeb")
    if run_cmd("python setup.py --command-packages=stdeb.command bdist_deb"):
        print("✅ .deb built successfully")
        return True
    return False

def build_dmg():
    """Build macOS .dmg"""
    print("🔨 Building macOS .dmg...")
    run_cmd("pip install pyinstaller")
    if run_cmd("pyinstaller --onefile --windowed dbl/__main__.py"):
        # For .dmg, need additional tools like create-dmg
        print("✅ .app built (use create-dmg for .dmg)")
        return True
    return False

def main():
    system = platform.system().lower()

    print(f"🏗️  Building DBL for {system}")

    # Always build wheel
    if not build_wheel():
        return 1

    if system == "windows":
        if not build_exe():
            return 1
    elif system == "linux":
        if not build_deb():
            return 1
    elif system == "darwin":  # macOS
        if not build_dmg():
            return 1

    print("🎉 All builds completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""Manifest management for branches and layers"""

import json
import os
from .constants import MANIFEST_FILE
from .utils import log


def load_manifest():
    """Load the manifest file containing branch information"""
    if not os.path.exists(MANIFEST_FILE):
        return {"current": "master", "branches": {"master": []}}
    
    with open(MANIFEST_FILE, 'r') as f: 
        data = json.load(f)
    
    # Migrate old format if needed
    if "layers" in data: 
        log("Migrating manifest to branch structure...", "warn")
        new_data = {"current": "master", "branches": {"master": data["layers"]}}
        save_manifest(new_data)
        return new_data
    
    return data


def save_manifest(data):
    """Save the manifest file"""
    with open(MANIFEST_FILE, 'w') as f: 
        json.dump(data, f, indent=2)

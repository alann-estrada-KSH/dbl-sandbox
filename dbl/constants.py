"""Constants and configuration paths for DBL"""

import os

# Version
VERSION = "0.0.1-alpha"

# File paths
CONFIG_FILE = "dbl.yaml"
DBL_DIR = ".dbl"
LAYERS_DIR = os.path.join(DBL_DIR, "layers")
SNAPSHOT_FILE = os.path.join(DBL_DIR, "snapshot.sql")
STATE_FILE = os.path.join(DBL_DIR, "state.json")
MANIFEST_FILE = os.path.join(LAYERS_DIR, "manifest.json")
SANDBOX_META_FILE = os.path.join(DBL_DIR, "sandbox.json")

# Colors
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

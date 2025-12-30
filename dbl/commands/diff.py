"""Diff command"""

import os
import json
import sys
from ..constants import STATE_FILE, SANDBOX_META_FILE
from ..config import load_config, get_engine
from ..state import get_target_db, get_state
from ..utils import log


def cmd_diff(args):
    """Detect database changes"""
    config = load_config()
    engine = get_engine(config)
    target_db, is_sandbox = get_target_db(config)
    
    current_state = get_state(engine, target_db, config)
    if not os.path.exists(STATE_FILE): 
        return False, []
    
    if is_sandbox:
        with open(SANDBOX_META_FILE) as f: 
            meta = json.load(f)
        baseline_state = get_state(engine, meta['backup_db'], config)
    else:
        with open(STATE_FILE) as f: 
            baseline_state = json.load(f)

    has_changes = False
    changed_data_tables = []
    
    if current_state['schema'] != baseline_state['schema']:
        log("🔴 SCHEMA CHANGE detected", "warn")
        has_changes = True
    
    for table, h in current_state['data'].items():
        if h != baseline_state['data'].get(table):
            log(f"🔴 DATA CHANGE: {table}", "warn")
            has_changes = True
            changed_data_tables.append(table)
            
    if not has_changes: 
        log(f"🟢 All clean in {target_db}", "success")
    
    sys.exit(0 if not has_changes else 1)

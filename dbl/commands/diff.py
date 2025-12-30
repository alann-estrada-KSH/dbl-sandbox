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
    
    # Filter tables if --tables specified
    filter_tables = args.tables if hasattr(args, 'tables') and args.tables else None
    if filter_tables:
        log(f"🔍 Filtering {len(filter_tables)} specific tables: {', '.join(filter_tables)}", "info")
    
    current_state = get_state(engine, target_db, config, filter_tables=filter_tables)
    
    if is_sandbox:
        with open(SANDBOX_META_FILE) as f: 
            meta = json.load(f)
        baseline_state = get_state(engine, meta['backup_db'], config, filter_tables=filter_tables)
    else:
        if not os.path.exists(STATE_FILE): 
            return False, []
        with open(STATE_FILE) as f: 
            baseline_state = json.load(f)

    has_changes = False
    changed_data_tables = []
    schema_changed = False
    
    if current_state['schema'] != baseline_state['schema']:
        log("🔴 SCHEMA CHANGE detected", "warn")
        log(f"   Current:  {current_state['schema'][:16]}...", "info")
        log(f"   Baseline: {baseline_state['schema'][:16]}...", "info")
        has_changes = True
        schema_changed = True
    
    # Check data changes
    all_tables = set(current_state['data'].keys()) | set(baseline_state['data'].keys())
    for table in sorted(all_tables):
        current_hash = current_state['data'].get(table)
        baseline_hash = baseline_state['data'].get(table)
        
        if current_hash != baseline_hash:
            if current_hash == "read_error" or baseline_hash == "read_error":
                log(f"⚠️  DATA ERROR: {table} (read failed)", "warn")
            elif current_hash is None:
                log(f"🔴 TABLE DROPPED: {table}", "warn")
            elif baseline_hash is None:
                log(f"🔴 TABLE ADDED: {table}", "warn")
            else:
                log(f"🔴 DATA CHANGE: {table}", "warn")
                log(f"   Current:  {current_hash[:16]}...", "info")
                log(f"   Baseline: {baseline_hash[:16]}...", "info")
            has_changes = True
            changed_data_tables.append(table)
            
    if not has_changes:
        log(f"🟢 All clean in {target_db}", "success")
        log(f"   Schema: {current_state['schema'][:16]}...", "info")
        log(f"   Tables tracked: {len(current_state['data'])}", "info")
    else:
        summary = []
        if schema_changed:
            summary.append("schema")
        if changed_data_tables:
            summary.append(f"{len(changed_data_tables)} table(s)")
        log(f"\n📊 Summary: Changes in {', '.join(summary)}", "warn")
    
    sys.exit(0 if not has_changes else 1)

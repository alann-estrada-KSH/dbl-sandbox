"""State management and comparison"""

import os
import json
import hashlib
from .constants import STATE_FILE, SANDBOX_META_FILE
from .utils import log, run_command
from .errors import DBLError
from .engines.postgres import PostgresEngine


def get_target_db(config):
    """Get target database and sandbox status"""
    is_sandbox = os.path.exists(SANDBOX_META_FILE)
    if is_sandbox:
        with open(SANDBOX_META_FILE) as f: 
            meta = json.load(f)
        log(f"🛡️  Sandbox Active (Backup: {meta['backup_db']})", "warn")
    return config['db_name'], is_sandbox


def get_state(engine, db_name, config):
    """Compute current DB state for comparison"""
    log(f"Analyzing state of: {db_name}...", "info")
    
    # 1. Schema State
    try:
        schema_dict = engine.inspect_db(db_name)
        schema_hash = hashlib.md5(json.dumps(schema_dict, sort_keys=True).encode()).hexdigest()
    except Exception as e:
        raise DBLError(f"Error inspeccionando esquema de '{db_name}': {e}")

    # 2. Data State (Tracked tables)
    whitelist = config.get('track_tables', [])
    blacklist = config.get('ignore_tables', [])
    
    all_tables = set(schema_dict.keys())
    if whitelist:
        track_tables = [t for t in whitelist if t in all_tables]
    else:
        track_tables = [t for t in all_tables if t not in blacklist]
        track_tables.sort()
    
    data_hashes = {}
    for table in track_tables:
        try:
            pk_cols = engine.get_primary_keys(db_name, table)
            if not pk_cols:
                log(f"Table {table} has no PK, skipping data tracking", "warn")
                continue
                
            order_by = ', '.join(pk_cols) if pk_cols else '1'
            query = f'SELECT * FROM {table} ORDER BY {order_by}'
            cmd = f'{engine.get_base_cmd(db_name)} -c "{query}"'
            data_raw = run_command(cmd, capture=True, 
                                  env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
            data_hashes[table] = hashlib.md5(data_raw.encode()).hexdigest()
        except Exception:
            data_hashes[table] = "read_error"

    return {"schema": schema_hash, "data": data_hashes}

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


def get_state(engine, db_name, config, filter_tables=None):
    """Compute current DB state for comparison"""
    log(f"Analyzing state of: {db_name}...", "info")
    
    # 1. Schema State
    try:
        schema_dict = engine.inspect_db(db_name)
        if not schema_dict:
            log(f"   WARNING: No tables detected in schema!", "warn")
            all_tables_check = engine.get_tables(db_name)
            if all_tables_check:
                log(f"   But get_tables() found {len(all_tables_check)} tables - possible INFORMATION_SCHEMA issue", "warn")
        schema_hash = hashlib.md5(json.dumps(schema_dict, sort_keys=True).encode()).hexdigest()
    except Exception as e:
        raise DBLError(f"Error inspeccionando esquema de '{db_name}': {e}")

    # 2. Data State (Tracked tables)
    whitelist = config.get('track_tables', [])
    blacklist = config.get('ignore_tables', [])
    
    all_tables = set(schema_dict.keys())
    
    # Apply filter_tables if specified
    if filter_tables:
        # Verify tables exist
        invalid_tables = [t for t in filter_tables if t not in all_tables]
        if invalid_tables:
            log(f"   ⚠️  Tables not found: {', '.join(invalid_tables)}", "warn")
        track_tables = [t for t in filter_tables if t in all_tables]
    elif whitelist:
        track_tables = [t for t in whitelist if t in all_tables]
    else:
        track_tables = [t for t in all_tables if t not in blacklist]
        track_tables.sort()
    
    data_hashes = {}
    tables_without_pk = []
    tables_with_errors = []
    
    log(f"   Schema: {len(schema_dict)} tables | Tracking: {len(track_tables)} tables", "info")
    
    from .utils import log_progress, clear_progress
    
    for idx, table in enumerate(track_tables, 1):
        # Show progress bar (truncate table name)
        table_display = table if len(table) <= 30 else table[:27] + "..."
        log_progress(idx, len(track_tables), "tables", f"- {table_display}")
        
        try:
            pk_cols = engine.get_primary_keys(db_name, table)
            if not pk_cols:
                tables_without_pk.append(table)
                # Fallback: use dump_table_data for tables without PK
                try:
                    data_raw = engine.dump_table_data(db_name, table)
                    if data_raw:
                        normalized = '\n'.join(line.strip() for line in data_raw.splitlines() if line.strip())
                        hash_val = hashlib.md5(normalized.encode('utf-8')).hexdigest()
                        data_hashes[table] = hash_val
                    else:
                        data_hashes[table] = "empty"
                except Exception as e:
                    tables_with_errors.append(f"{table} (fallback failed)")
                    data_hashes[table] = "read_error"
                continue
                
            order_by = ', '.join(pk_cols) if pk_cols else '1'
            query = f'SELECT * FROM {table} ORDER BY {order_by}'
            cmd = engine.execute_query(db_name, query)
            data_raw = run_command(cmd, capture=True, 
                                  env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
            
            # Normalize data before hashing (strip whitespace, normalize newlines)
            normalized = '\n'.join(line.strip() for line in data_raw.splitlines() if line.strip())
            hash_val = hashlib.md5(normalized.encode('utf-8')).hexdigest()
            data_hashes[table] = hash_val
            
        except Exception as e:
            tables_with_errors.append(f"{table} ({str(e)[:50]})")
            data_hashes[table] = "read_error"
    
    # Clear progress line and show summary
    clear_progress()
    log(f"   ✓ Tracked: {len(data_hashes)} tables successfully", "info")
    if tables_without_pk:
        log(f"   ⚠️  {len(tables_without_pk)} tables without PK (using fallback): {', '.join(tables_without_pk[:5])}{'...' if len(tables_without_pk) > 5 else ''}", "warn")
    if tables_with_errors:
        log(f"   ❌ {len(tables_with_errors)} tables with errors: {', '.join(tables_with_errors[:3])}{'...' if len(tables_with_errors) > 3 else ''}", "error")

    return {"schema": schema_hash, "data": data_hashes}

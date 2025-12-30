"""Commit command"""

import os
import json
import time
import subprocess
import tempfile
from ..constants import SANDBOX_META_FILE, LAYERS_DIR
from ..config import load_config, get_engine
from ..state import get_target_db
from ..manifest import load_manifest, save_manifest
from ..planner import generate_migration_sql
from ..utils import log


def cmd_commit(args):
    """Commit changes as a new layer"""
    config = load_config()
    engine = get_engine(config)
    db, is_sandbox = get_target_db(config)
    
    if not is_sandbox: 
        return log("You must be in sandbox: dbl sandbox start", "error")
    
    with open(SANDBOX_META_FILE) as f: 
        meta = json.load(f)
    backup_db = meta['backup_db']
    
    include_data = args.with_data if hasattr(args, 'with_data') and args.with_data else False
    
    # Generate migration SQL
    sql = generate_migration_sql(config, engine, db, backup_db, include_data=include_data)
    
    # Check if there is actual SQL
    clean_lines = [l for l in sql.splitlines() if not l.strip().startswith("--") and l.strip()]
    if not clean_lines:
        return log("No structural or data changes detected.", "warn")
    
    # Open editor
    with tempfile.NamedTemporaryFile(suffix=".sql", mode='w+', delete=False) as tf:
        tf.write(sql)
        tpath = tf.name
    
    editor = os.environ.get('EDITOR', 'nano')
    try: 
        subprocess.call([editor, tpath])
    except: 
        pass
    
    with open(tpath, 'r') as f: 
        final_sql = f.read().strip()
    os.remove(tpath)
    
    if not final_sql or len([l for l in final_sql.splitlines() if not l.strip().startswith("--")]) == 0:
        return log("Commit canceled (empty SQL).", "warn")
        
    # Save layer
    manifest = load_manifest()
    curr = manifest['current']
    fname = f"{curr}_{int(time.time())}.sql"
    
    with open(os.path.join(LAYERS_DIR, fname), 'w') as f:
        f.write(f"-- {args.message}\n{final_sql}")
    
    # Add commit metadata
    commit_info = {"file": fname, "msg": args.message}
    if include_data:
        commit_info["type"] = "schema+data"
    else:
        commit_info["type"] = "schema"
    
    manifest['branches'][curr].append(commit_info)
    save_manifest(manifest)
    
    log(f"Capa guardada: {fname} ({commit_info['type']})", "success")
    log("Syncing shadow DB...", "info")
    engine.drop_db(backup_db)
    engine.clone_db(db, backup_db)

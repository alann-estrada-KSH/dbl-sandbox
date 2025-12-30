"""Reset command"""

import os
from ..constants import SNAPSHOT_FILE, LAYERS_DIR
from ..config import load_config, get_engine
from ..state import get_target_db
from ..manifest import load_manifest
from ..utils import log, confirm_action, run_command
from ..engines.postgres import PostgresEngine


def cmd_reset(args):
    """Rebuild database from layers"""
    config = load_config()
    engine = get_engine(config)
    db, is_sandbox = get_target_db(config)
    m = load_manifest()
    
    if not is_sandbox:
        if not confirm_action(f"This will rebuild database '{db}'. Continue?"):
            return
    
    log(f"Rebuilding {db} on branch {m['current']}...", "warn")
    engine.drop_db(db)
    engine.create_db(db)
    
    if os.path.exists(SNAPSHOT_FILE):
        run_command(f"cat {SNAPSHOT_FILE} | {engine.get_base_cmd(db)}", 
                   env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
        
    for l in m['branches'][m['current']]:
        path = os.path.join(LAYERS_DIR, l['file'])
        run_command(f"cat {path} | {engine.get_base_cmd(db)}", 
                   env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
    
    log("State restored.", "success")

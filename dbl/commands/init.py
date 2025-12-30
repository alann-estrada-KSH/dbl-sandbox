"""Init and import commands"""

import os
import yaml
from ..constants import CONFIG_FILE, LAYERS_DIR, SNAPSHOT_FILE
from ..utils import log, confirm_action, run_command
from ..config import load_config, get_engine
from ..manifest import save_manifest
from ..engines.postgres import PostgresEngine


def cmd_init(args):
    """Initialize DBL project"""
    if os.path.exists(CONFIG_FILE): 
        return log("dbl.yaml already exists", "warn")
    
    os.makedirs(LAYERS_DIR, exist_ok=True)
    config = {
        "engine": "postgres", 
        "container_name": "", 
        "host": "localhost", 
        "port": 5432,
        "db_name": "myapp", 
        "user": "postgres", 
        "password": "password",
        "ignore_tables": ["migrations", "failed_jobs", "sessions"], 
        "policies": { 
            "allow_drop_table": False, 
            "allow_drop_column": False  
        }
    }
    with open(CONFIG_FILE, 'w') as f: 
        yaml.dump(config, f)
    
    save_manifest({"current": "master", "branches": {"master": []}})
    log(f"Created {CONFIG_FILE}. Initial branch: master", "success")
    log(f"Please review and adjust configuration before proceeding.", "info")


def cmd_import(args):
    """Import SQL snapshot"""
    config = load_config()
    engine = get_engine(config)
    db = config['db_name']
    
    if not confirm_action(f"This will import the snapshot and recreate database '{db}'. Continue?"):
        return
    
    run_command(f"cp {args.file} {SNAPSHOT_FILE}")
    engine.drop_db(db)
    engine.create_db(db)
    run_command(f"cat {SNAPSHOT_FILE} | {engine.get_base_cmd(db)}", 
               env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
    save_manifest({"current": "master", "branches": {"master": []}})
    log("Snapshot imported. Master reset.", "success")

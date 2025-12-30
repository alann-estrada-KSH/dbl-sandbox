"""Sandbox commands"""

import os
import json
import time
from ..constants import SANDBOX_META_FILE
from ..config import load_config, get_engine
from ..manifest import load_manifest
from ..utils import log


def cmd_sandbox(args):
    """Manage sandbox environment"""
    config = load_config()
    engine = get_engine(config)
    db = config['db_name']
    
    if args.action == "start":
        if os.path.exists(SANDBOX_META_FILE): 
            return log("Sandbox already active.", "error")
        
        bk = f"{db}_dbl_shadow_{int(time.time())}"
        log("🛡️  Creating safe environment (Sandbox)...", "header")
        engine.backup_db(db, bk)
        
        with open(SANDBOX_META_FILE, 'w') as f:
            json.dump({"mode":"shadow","active_db":db,"backup_db":bk}, f)
        
        log("✅ Sandbox ready. You can work locally as usual.", "success")
        
    elif args.action == "rollback":
        if not os.path.exists(SANDBOX_META_FILE): 
            return log("No sandbox active.", "error")
        
        with open(SANDBOX_META_FILE) as f: 
            meta = json.load(f)
        
        log("🔙 Reverting changes...", "warn")
        engine.drop_db(meta['active_db'])
        engine.clone_db(meta['backup_db'], meta['active_db'])
        engine.drop_db(meta['backup_db'])
        os.remove(SANDBOX_META_FILE)
        log("DB restored to original state.", "success")
        
    elif args.action == "apply":
        if not os.path.exists(SANDBOX_META_FILE): 
            return log("No sandbox active.", "error")

        with open(SANDBOX_META_FILE) as f: 
            meta = json.load(f)
        
        log("💾 Confirming changes (Sandbox closed)...", "success")
        engine.drop_db(meta['backup_db'])
        os.remove(SANDBOX_META_FILE)

    elif args.action == "status":
        if os.path.exists(SANDBOX_META_FILE):
            with open(SANDBOX_META_FILE) as f: 
                meta = json.load(f)
            log(f"Sandbox Active: {meta['active_db']} (Shadow: {meta['backup_db']})", "branch")
        else:
            m = load_manifest()
            log(f"Current branch: {m['current']}", "info")

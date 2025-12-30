"""Branch-related commands"""

import os
from datetime import datetime
from ..constants import LAYERS_DIR
from ..manifest import load_manifest, save_manifest
from ..config import load_config, get_engine
from ..state import get_target_db
from ..errors import DBLError
from ..utils import log, run_command
from ..engines.postgres import PostgresEngine


def cmd_branch(args):
    """List, create, or delete branches"""
    m = load_manifest()
    
    if args.delete:
        if args.delete == m['current']: 
            return log("You cannot delete the current branch", "error")
        if args.delete in m['branches']: 
            del m['branches'][args.delete]
            save_manifest(m)
            log(f"Branch {args.delete} deleted", "success")
    elif args.name:
        if args.name in m['branches']: 
            return log("Branch already exists", "error")
        
        # Create new branch from current
        m['branches'][args.name] = list(m['branches'][m['current']])
        
        # Store metadata
        if '_metadata' not in m:
            m['_metadata'] = {}
        m['_metadata'][args.name] = {
            "parent": m['current'], 
            "created_at": datetime.now().isoformat()
        }
        save_manifest(m)
        log(f"Branch {args.name} created (parent: {m['current']})", "success")
    else:
        for b in m['branches']:
            parent = ""
            if '_metadata' in m and b in m['_metadata']:
                parent = f" <- {m['_metadata'][b]['parent']}"
            log(f"{'*' if b == m['current'] else ' '} {b}{parent}", "branch")


def cmd_checkout(args):
    """Switch branch and rebuild DB"""
    config = load_config()
    _, is_sandbox = get_target_db(config)
    
    if is_sandbox:
        raise DBLError("Sandbox mode active. Do 'commit' or 'rollback' before switching branches.")
    
    manifest = load_manifest()
    target_branch = args.branch
    
    if target_branch not in manifest['branches']:
        raise DBLError(f"Branch '{target_branch}' does not exist. Use 'dbl branch <name>' to create it.")
    
    if target_branch == manifest['current']:
        log(f"Already on branch '{target_branch}'.", "info")
        return

    # Update pointer
    manifest['current'] = target_branch
    save_manifest(manifest)
    log(f"Switching to branch '{target_branch}'...", "branch")
    
    # Rebuild DB
    from .reset import cmd_reset
    cmd_reset(args)


def cmd_merge(args):
    """Merge changes from another branch"""
    m = load_manifest()
    curr, tgt = m['current'], args.branch
    
    if tgt not in m['branches']: 
        return log("Target branch does not exist", "error")
    
    curr_files = {l['file'] for l in m['branches'][curr]}
    new_layers = [l for l in m['branches'][tgt] if l['file'] not in curr_files]
    
    if not new_layers: 
        return log("Nothing to merge.", "info")
    
    config = load_config()
    engine = get_engine(config)
    db = config['db_name']
    
    for l in new_layers:
        log(f"Applying {l['file']}", "info")
        path = os.path.join(LAYERS_DIR, l['file'])
        run_command(f"cat {path} | {engine.get_base_cmd(db)}", 
                   env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
        m['branches'][curr].append(l)
    
    save_manifest(m)
    log("Merge completed.", "success")


def cmd_pull(args):
    """Pull changes from another branch"""
    m = load_manifest()
    curr = m['current']
    src = args.branch
    
    if src not in m['branches']:
        return log(f"Branch '{src}' does not exist", "error")
    
    if src == curr:
        return log(f"Already on branch '{src}'.", "info")
    
    config = load_config()
    engine = get_engine(config)
    db = config['db_name']
    
    # Get new layers
    curr_files = {l['file'] for l in m['branches'][curr]}
    new_layers = [l for l in m['branches'][src] if l['file'] not in curr_files]
    
    if not new_layers:
        return log(f"No new changes from '{src}'", "info")
    
    log(f"Pulling {len(new_layers)} layers from branch '{src}'...", "info")
    for l in new_layers:
        log(f"  Applying: {l['file']}", "info")
        path = os.path.join(LAYERS_DIR, l['file'])
        run_command(f"cat {path} | {engine.get_base_cmd(db)}", 
                   env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
        m['branches'][curr].append(l)
    
    save_manifest(m)
    log(f"Pull from '{src}' completed. Branch '{curr}' updated.", "success")

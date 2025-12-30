"""Rebase command"""

import datetime
from ..manifest import load_manifest, save_manifest
from ..utils import log


def cmd_rebase(args):
    """Rebase current branch onto another"""
    m = load_manifest()
    curr = m['current']
    onto = args.onto
    
    if onto not in m['branches']:
        return log(f"Base branch '{onto}' does not exist", "error")

    base_layers = list(m['branches'][onto])
    curr_layers = list(m['branches'][curr])
    base_files = {l['file'] for l in base_layers}

    new_layers = base_layers + [l for l in curr_layers if l['file'] not in base_files]
    skipped = [l for l in curr_layers if l['file'] in base_files]

    if args.dry_run:
        log("Rebase (dry-run):", "info")
        log(f"  Base: {onto} ({len(base_layers)} layers)", "info")
        log(f"  Current: {curr} ({len(curr_layers)} layers)", "info")
        log(f"  Result: {len(new_layers)} layers", "info")
        if skipped:
            log(f"  Skipped due to duplicates: {len(skipped)}", "warn")
        return

    # Backup
    if not args.no_backup:
        ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        backup_name = f"{curr}_backup_{ts}"
        m['branches'][backup_name] = list(curr_layers)
        log(f"Backup created: {backup_name}", "info")

    m['branches'][curr] = new_layers
    save_manifest(m)
    log(f"Rebase completed: '{curr}' onto '{onto}'.", "success")
    log("Tip: run 'dbl reset' to rebuild the DB.", "info")

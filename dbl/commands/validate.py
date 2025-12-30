"""Validate command"""

import os
import sys
from ..constants import LAYERS_DIR
from ..config import load_config
from ..manifest import load_manifest
from ..utils import log


def cmd_validate(args):
    """Validate phases without blocking"""
    try:
        config = load_config()
    except Exception:
        config = {}
    
    vcfg = (config or {}).get('validate', {})
    strict = bool(vcfg.get('strict', False))
    allow_orphaned = bool(vcfg.get('allow_orphaned', False))
    require_comments = bool(vcfg.get('require_comments', False))
    detect_type_changes = bool(vcfg.get('detect_type_changes', True))

    m = load_manifest()
    branch = args.branch if hasattr(args, 'branch') and args.branch else m['current']
    
    if branch not in m['branches']:
        return log(f"Branch '{branch}' does not exist", "error")
    
    layers = m['branches'][branch]
    
    if not layers:
        log(f"Branch '{branch}' is empty", "info")
        return
    
    warnings = []
    errors = []
    phases_seen = {}
    
    for i, layer in enumerate(layers):
        layer_path = os.path.join(LAYERS_DIR, layer['file'])
        
        try:
            with open(layer_path, 'r') as f:
                content = f.read()
        except:
            warnings.append(f"⚠️  Could not read: {layer['file']}")
            continue
        
        lines = content.splitlines()
        layer_phases = set()
        has_set_not_null = False
        has_drop = False
        has_uncommented_drop_here = False
        has_data_sync = False
        has_type_change = False
        
        for line in lines:
            stripped = line.strip()
            
            if "-- phase: expand" in stripped:
                layer_phases.add('expand')
            elif "-- phase: backfill" in stripped:
                layer_phases.add('backfill')
            elif "-- phase: contract" in stripped:
                layer_phases.add('contract')
            
            if "SET NOT NULL" in stripped and not stripped.startswith("--"):
                has_set_not_null = True
            
            if "DROP TABLE" in stripped or "DROP COLUMN" in stripped:
                has_drop = True
                if not stripped.startswith("--"):
                    has_uncommented_drop_here = True
            
            if "TRUNCATE TABLE" in stripped and not stripped.startswith("--"):
                has_data_sync = True

            if detect_type_changes:
                if ("ALTER TABLE" in stripped and "ALTER COLUMN" in stripped and 
                    (" TYPE " in stripped or " SET DATA TYPE " in stripped)) and not stripped.startswith("--"):
                    has_type_change = True
                if ("ALTER TABLE" in stripped and " MODIFY " in stripped) and not stripped.startswith("--"):
                    has_type_change = True
        
        # Validations
        if 'contract' in layer_phases and 'backfill' not in layer_phases:
            had_backfill_before = 'backfill' in phases_seen
            if not had_backfill_before:
                msg = f"Layer {layer['file']}: Contract without prior backfill"
                (errors if strict else warnings).append(f"⚠️  {msg}" if not strict else f"❌ {msg}")

        if 'backfill' in layer_phases:
            had_expand_before = 'expand' in phases_seen
            if not had_expand_before and not allow_orphaned:
                warnings.append(f"⚠️  Layer {layer['file']}: Backfill without prior expand")
        
        if has_uncommented_drop_here:
            msg = f"Layer {layer['file']}: DROP not commented"
            (errors if strict and require_comments else warnings).append(
                f"⚠️  {msg}" if not (strict and require_comments) else f"❌ {msg}")
        
        if has_set_not_null:
            has_data_op_before = any("UPDATE" in l or "INSERT INTO" in l 
                                    for l in lines if not l.strip().startswith("--"))
            if not has_data_op_before:
                msg = f"Layer {layer['file']}: SET NOT NULL without prior UPDATE/INSERT"
                (errors if strict else warnings).append(f"⚠️  {msg}" if not strict else f"❌ {msg}")
        
        if has_data_sync:
            if 'expand' in layer_phases or 'contract' in layer_phases:
                warnings.append(f"⚠️  Layer {layer['file']}: TRUNCATE + ALTER TABLE mixed")
        
        layer_type = layer.get('type', 'unknown')
        if has_data_sync and layer_type == 'schema':
            warnings.append(f"⚠️  Layer {layer['file']}: Has TRUNCATE but marked as 'schema'")

        if detect_type_changes and has_type_change:
            warnings.append(f"⚠️  Layer {layer['file']}: Column type change detected")
        
        phases_seen.update({p: i for p in layer_phases})
    
    if hasattr(args, 'fix') and args.fix:
        log("🔧 Autofix not implemented (planned for v0.5)", "warn")
    
    total_warn = len(warnings)
    total_err = len(errors)
    
    if total_warn == 0 and total_err == 0:
        log(f"✅ Branch '{branch}' valid (no anomalies detected)", "success")
        return
    
    if total_err > 0:
        log(f"❌ Validation for branch '{branch}': {total_err} error(s)", "error")
    if total_warn > 0:
        log(f"⚠️  Validation for branch '{branch}': {total_warn} warning(s)", "warn")
    
    print("")
    for e in errors:
        print(f"   {e}")
    for w in warnings:
        print(f"   {w}")
    print("")
    
    log("💡 Rule: Validate reports, does not execute.", "info")
    if strict and total_err > 0:
        sys.exit(1)

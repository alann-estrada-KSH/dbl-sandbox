"""Log and rev-parse commands"""

import hashlib
from ..manifest import load_manifest
from ..utils import log


def cmd_log(args):
    """Show layer history"""
    m = load_manifest()
    branch = args.branch if hasattr(args, 'branch') and args.branch else m['current']
    
    if branch not in m['branches']:
        return log(f"Branch '{branch}' does not exist", "error")
    
    layers = m['branches'][branch]
    
    if not layers:
        return log(f"No layers in branch '{branch}'", "info")
    
    limit = args.n if hasattr(args, 'n') and args.n else len(layers)
    oneline = args.oneline if hasattr(args, 'oneline') else False
    
    # Show in reverse order (most recent first)
    for i, layer in enumerate(reversed(layers[-limit:])):
        if oneline:
            layer_hash = hashlib.md5(layer['file'].encode()).hexdigest()[:7]
            print(f"{layer_hash} {layer['msg']}")
        else:
            log(f"Layer: {layer['file']}", "branch")
            log(f"  Message: {layer['msg']}", "info")


def cmd_rev_parse(args):
    """Resolve references"""
    m = load_manifest()
    ref = args.ref.lower() if hasattr(args, 'ref') else 'head'
    
    if ref == 'head':
        print(m['current'])
    else:
        if ref in m['branches']:
            print(f"{ref}")
        else:
            log(f"Reference '{ref}' not found", "error")

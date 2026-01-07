"""Help and version commands"""

from ..constants import VERSION
from ..utils import log


def cmd_version(args):
    """Show version information"""
    log(f"DBL (Database Layering) v{VERSION}", "header")
    log("Repository: https://github.com/alann-estrada-KSH/dbl-sandbox", "info")


def cmd_help(args):
    """Show help information"""
    log("Available commands:", "info")
    print("  -v, --version                         (Show version and exit)")
    print("  init                                  (Initialize DBL project)")
    print("  import <file>                         (Import SQL snapshot)")
    print("  sandbox                               (Create/manage safe sandbox)")
    print("    - start                             (Create sandbox)")
    print("    - apply                             (Confirm changes)")
    print("    - rollback                          (Discard changes)")
    print("    - status                            (Show status)")
    print("  diff                                  (Detect DB changes)")
    print("  commit -m <msg> [--with-data]         (Save layer; data is opt-in)")
    print("  reset                                 (Rebuild DB from layers)")
    print("  branch [name] [-d name]               (List, create or delete branches)")
    print("  checkout <branch>                     (Switch branch and rebuild DB)")
    print("  merge <branch>                        (Merge changes from another branch)")
    print("  pull <branch>                         (Pull changes from another branch)")
    print("  log [branch] [--oneline] [-n N]       (Show layer history)")
    print("  rev-parse <ref>                       (Resolve references)")
    print("  rebase <onto> [--dry-run]             (Rebase current branch)")
    print("  validate [branch]                     (Validate phases (non-blocking))")
    print("  update [-y]                           (Check and install updates)")
    print("  version                               (Show version information)")
    print("  help                                  (Show this help)")
    print("")
    print("💡 Migration phases (optional metadata):")
    print("   expand:    Add columns/tables (safe)")
    print("   backfill:  Update data (requires --with-data)")
    print("   contract:  Remove/constrain (review before executing)")
    print("")
    print("🔧 Configurable validation (dbl.yaml → validate):")
    print("   strict: false              (true = warnings treated as errors)")
    print("   allow_orphaned: false      (true = allow backfill without expand)")
    print("   require_comments: false    (true = require comments for contract)")
    print("   detect_type_changes: true  (warn about type changes)")

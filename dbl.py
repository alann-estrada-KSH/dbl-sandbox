#!/usr/bin/env python3
"""
DBL - Database Layering
Git-like version control for databases
"""

import sys
import argparse
from dbl.constants import VERSION, Color
from dbl.errors import InvalidCommandError, DBLError
from dbl.utils import log
from dbl.commands import (
    cmd_help, cmd_version, cmd_init, cmd_import, cmd_sandbox,
    cmd_diff, cmd_commit, cmd_reset, cmd_branch, cmd_checkout,
    cmd_merge, cmd_pull, cmd_log, cmd_rev_parse, cmd_rebase, cmd_validate,
    cmd_update
)


class CustomParser(argparse.ArgumentParser):
    """Custom argument parser with better error messages"""
    
    def error(self, message):
        if "invalid choice" in message:
            raise InvalidCommandError()
        if "required: cmd" in message or "the following arguments are required: cmd" in message:
            log("No command specified.", "error")
            log("Use 'dbl help' to see available commands.", "info")
            log(f"Or visit: {Color.OKCYAN}https://github.com/alann-estrada-KSH/dbl-sandbox{Color.ENDC}", "info")
            sys.exit(1)
        super().error(message)


def main():
    """Main entry point"""
    parser = CustomParser(description="DBL - Database Layering")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    # Basic commands
    sub.add_parser("help")
    sub.add_parser("version")
    sub.add_parser("init")
    sub.add_parser("import").add_argument("file")
    
    # Sandbox commands
    sb = sub.add_parser("sandbox")
    sb_act = sb.add_subparsers(dest="action", required=True)
    sb_act.add_parser("start")
    sb_act.add_parser("rollback")
    sb_act.add_parser("apply")
    sb_act.add_parser("status")
    
    # Diff and commit
    sub.add_parser("diff")
    com_p = sub.add_parser("commit")
    com_p.add_argument("-m", "--message", required=True)
    com_p.add_argument("--with-data", action="store_true", help="Include data sync (opt-in)")
    
    # Branch commands
    br = sub.add_parser("branch")
    br.add_argument("name", nargs="?", help="New branch name")
    br.add_argument("-d", "--delete", help="Branch name to delete")
    
    sub.add_parser("checkout").add_argument("branch", help="Branch name to switch to")
    sub.add_parser("merge").add_argument("branch", help="Branch name to merge")
    sub.add_parser("pull").add_argument("branch", help="Branch name to pull from")
    
    # Rebase
    re_p = sub.add_parser("rebase", help="Rebase current branch")
    re_p.add_argument("onto", help="Target base branch")
    re_p.add_argument("--dry-run", action="store_true", help="Show result without applying")
    re_p.add_argument("--no-backup", action="store_true", help="Do not create backup branch")
    
    # Log
    log_p = sub.add_parser("log", help="View layer history")
    log_p.add_argument("branch", nargs="?", help="Branch to view (default: current)")
    log_p.add_argument("--oneline", action="store_true", help="Short format")
    log_p.add_argument("-n", type=int, help="Number of layers to show")
    
    # Rev-parse
    rev_p = sub.add_parser("rev-parse", help="Resolve references")
    rev_p.add_argument("ref", help="Reference to resolve (HEAD, branch, etc)")
    
    # Reset
    sub.add_parser("reset")

    # Validate
    val = sub.add_parser("validate", help="Validate anomalies in layers")
    val.add_argument("branch", nargs="?", help="Branch to validate (optional, uses current)")
    val.add_argument("--fix", action="store_true", help="(Future) Attempt safe autofix")

    # Update
    upd = sub.add_parser("update", help="Check for updates and install them")
    upd.add_argument("-y", "--yes", action="store_true", help="Auto-confirm update installation")

    try:
        args = parser.parse_args()
        
        # Route to appropriate command
        if args.cmd == "init": cmd_init(args)
        elif args.cmd == "version": cmd_version(args)
        elif args.cmd == "import": cmd_import(args)
        elif args.cmd == "sandbox": cmd_sandbox(args)
        elif args.cmd == "diff": cmd_diff(args)
        elif args.cmd == "commit": cmd_commit(args)
        elif args.cmd == "reset": cmd_reset(args)
        elif args.cmd == "branch": cmd_branch(args)
        elif args.cmd == "checkout": cmd_checkout(args)
        elif args.cmd == "merge": cmd_merge(args)
        elif args.cmd == "pull": cmd_pull(args)
        elif args.cmd == "log": cmd_log(args)
        elif args.cmd == "rev-parse": cmd_rev_parse(args)
        elif args.cmd == "rebase": cmd_rebase(args)
        elif args.cmd == "validate": cmd_validate(args)
        elif args.cmd == "update": cmd_update(args)
        elif args.cmd == "help": cmd_help(args)
        else: cmd_help(args)

    except InvalidCommandError: 
        log("Invalid command. Type 'dbl help' to see available commands.", "error")
    except DBLError as e: 
        log(str(e), "error")
    except KeyboardInterrupt: 
        print("\n")
    except Exception as e: 
        log(f"Error inesperado: {e}", "error")


if __name__ == "__main__": 
    main()

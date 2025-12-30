#!/usr/bin/env python3
import argparse
import subprocess
import yaml
import json
import os
import hashlib
import sys
import datetime
import time
import tempfile
from datetime import datetime
from abc import ABC, abstractmethod

# --- VERSION ---
VERSION = "0.0.1-alpha"

# --- CONSTANTS & PATHS ---
CONFIG_FILE = "dbl.yaml"
DBL_DIR = ".dbl"
LAYERS_DIR = os.path.join(DBL_DIR, "layers")
SNAPSHOT_FILE = os.path.join(DBL_DIR, "snapshot.sql")
STATE_FILE = os.path.join(DBL_DIR, "state.json")
MANIFEST_FILE = os.path.join(LAYERS_DIR, "manifest.json")
SANDBOX_META_FILE = os.path.join(DBL_DIR, "sandbox.json")

# --- COLORS & UTILITIES ---
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(msg, type="info"):
    if type == "header": print(f"{Color.HEADER}🚀 {msg}{Color.ENDC}")
    elif type == "success": print(f"{Color.OKGREEN}✅ {msg}{Color.ENDC}")
    elif type == "warn": print(f"{Color.WARNING}⚠️  {msg}{Color.ENDC}")
    elif type == "error": print(f"{Color.FAIL}❌ {msg}{Color.ENDC}")
    elif type == "branch": print(f"{Color.OKCYAN}🌿 {msg}{Color.ENDC}")
    elif type == "info": print(f"ℹ️  {msg}{Color.ENDC}")
    else: print(msg)

class DBLError(Exception): pass
class InvalidCommandError(Exception): pass

class CustomParser(argparse.ArgumentParser):
    def error(self, message):
        if "invalid choice" in message:
            raise InvalidCommandError()
        if "required: cmd" in message or "the following arguments are required: cmd" in message:
            log("No command specified.", "error")
            log("Use 'dbl help' to see available commands.", "info")
            log(f"Or visit: {Color.OKCYAN}https://github.com/alann-estrada-KSH/dbl-sandbox{Color.ENDC}", "info")
            sys.exit(1)
        super().error(message)

def confirm_action(message):
    try:
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print()
        return False

def run_command(cmd, capture=False, env=None):
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            env=env
        )
        return result.stdout.strip() if capture else None
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        raise DBLError(f"Failed internal command.\n   Cmd: {cmd}\n   Err: {error_msg}")

# --- MANIFEST MANAGEMENT (BRANCHES) ---
def load_manifest():
    if not os.path.exists(MANIFEST_FILE):
        return {"current": "master", "branches": {"master": []}}
    with open(MANIFEST_FILE, 'r') as f: data = json.load(f)
    if "layers" in data: 
        log("Migrating manifest to branch structure...", "warn")
        new_data = {"current": "master", "branches": {"master": data["layers"]}}
        save_manifest(new_data)
        return new_data
    return data

def save_manifest(data):
    with open(MANIFEST_FILE, 'w') as f: json.dump(data, f, indent=2)

# --- ENGINE ABSTRACTION (ENGINE & INSPECTOR) ---
class DBEngine(ABC):
    def __init__(self, config):
        self.host = config.get('host', 'localhost')
        self.port = str(config.get('port', '5432'))
        self.user = config.get('user', 'postgres')
        self.password = config.get('password', '')
        self.container = config.get('container_name')
        self.is_docker = bool(self.container)

    @abstractmethod
    def get_base_cmd(self, db_name=None): pass
    @abstractmethod
    def get_admin_db_name(self): pass
    @abstractmethod
    def drop_db(self, db_name): pass
    @abstractmethod
    def create_db(self, db_name): pass
    @abstractmethod
    def clone_db(self, source_db, target_db): pass
    @abstractmethod
    def get_tables(self, db_name): pass
    
    # --- INSPECTOR (AST Generator) ---
    @abstractmethod
    def inspect_db(self, db_name): pass
    @abstractmethod
    def dump_table_create(self, db_name, table): pass
    @abstractmethod
    def dump_table_data(self, db_name, table): pass
    
    # --- SQL GENERATORS (Dialect Specific) ---
    @abstractmethod
    def get_alter_column_type_sql(self, table, col, new_type): pass
    @abstractmethod
    def get_set_not_null_sql(self, table, col, col_type): pass
    @abstractmethod
    def get_drop_column_sql(self, table, col): pass
    @abstractmethod
    def get_primary_keys(self, db_name, table): pass

    def backup_db(self, source_db, backup_db):
        self.clone_db(source_db, backup_db)

class PostgresEngine(DBEngine):
    def _docker_prefix(self):
        return f"docker exec -i {self.container} " if self.is_docker else ""
    def _auth_env(self):
        env = os.environ.copy()
        if not self.is_docker: env['PGPASSWORD'] = self.password
        return env
    def get_base_cmd(self, db_name=None):
        target = db_name if db_name else "postgres"
        cmd = f"psql -h {self.host} -p {self.port} -U {self.user} -d {target} -v ON_ERROR_STOP=1"
        return self._docker_prefix() + cmd
    def get_admin_db_name(self): return "postgres"

    def drop_db(self, db_name):
        kill = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db_name}' AND pid <> pg_backend_pid();"
        run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "{kill}"', env=self._auth_env())
        run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "DROP DATABASE IF EXISTS {db_name};"', env=self._auth_env())
    
    def create_db(self, db_name):
        run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "CREATE DATABASE {db_name};"', env=self._auth_env())

    def clone_db(self, source, target):
        log(f"Clonando {source} -> {target}...", "info")
        try:
            kill = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{source}' AND pid <> pg_backend_pid();"
            run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "{kill}"', env=self._auth_env())
            run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "CREATE DATABASE {target} WITH TEMPLATE {source};"', env=self._auth_env())
        except Exception:
            log("Fallback a pg_dump (Clone lento)...", "warn")
            self.create_db(target)
            dump = f"pg_dump -h {self.host} -p {self.port} -U {self.user} {source}"
            if self.is_docker: dump = f"docker exec {self.container} {dump}"
            run_command(f"{dump} | {self.get_base_cmd(target)}", env=self._auth_env())

    def get_tables(self, db_name):
        cmd = f'{self.get_base_cmd(db_name)} -t -c "SELECT tablename FROM pg_tables WHERE schemaname=\'public\';"'
        out = run_command(cmd, capture=True, env=self._auth_env())
        return [line.strip() for line in out.splitlines() if line.strip()]

    def inspect_db(self, db_name):
        # Improved Inspector: Captures Defaults + Length/Precision
        query = """
            SELECT table_name, column_name, data_type, is_nullable, column_default,
                   character_maximum_length, numeric_precision, numeric_scale
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            ORDER BY table_name, ordinal_position;
        """
        cmd = f'{self.get_base_cmd(db_name)} -t -A -F "|" -c "{query}"'
        out = run_command(cmd, capture=True, env=self._auth_env())
        
        schema = {}
        if not out: return schema
        
        for line in out.splitlines():
            if not line.strip(): continue
            parts = line.split("|")
            if len(parts) < 8: continue
            
            t_name, c_name, dtype, nullable = parts[0], parts[1], parts[2], parts[3]
            default_val = parts[4] if len(parts) > 4 else None
            char_len = parts[5] if len(parts) > 5 and parts[5] not in (None, '', 'NULL') else None
            num_prec = parts[6] if len(parts) > 6 and parts[6] not in (None, '', 'NULL') else None
            num_scale = parts[7] if len(parts) > 7 and parts[7] not in (None, '', 'NULL') else None
            
            if t_name not in schema: schema[t_name] = {}
            
            schema[t_name][c_name] = {
                "type": dtype,
                "length": int(char_len) if char_len else None,
                "precision": int(num_prec) if num_prec else None,
                "scale": int(num_scale) if num_scale else None,
                "nullable": nullable == "YES",
                "default": default_val
            }
        return schema

    def dump_table_create(self, db_name, table):
        dump = f"pg_dump -h {self.host} -p {self.port} -U {self.user} --schema-only --table=public.{table} {db_name}"
        if self.is_docker: dump = f"docker exec {self.container} {dump}"
        sql = run_command(dump, capture=True, env=self._auth_env())
        # Make CREATE TABLE idempotent
        if sql:
            sql = sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
        return sql

    def dump_table_data(self, db_name, table):
        dump = f"pg_dump -h {self.host} -p {self.port} -U {self.user} --data-only --column-inserts --table=public.{table} {db_name}"
        if self.is_docker: dump = f"docker exec {self.container} {dump}"
        return run_command(dump, capture=True, env=self._auth_env())
    
    def get_primary_keys(self, db_name, table):
        query = f"""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{table}'::regclass AND i.indisprimary
            ORDER BY array_position(i.indkey, a.attnum);
        """
        cmd = f'{self.get_base_cmd(db_name)} -t -c "{query}"'
        out = run_command(cmd, capture=True, env=self._auth_env())
        return [line.strip() for line in out.splitlines() if line.strip()]

    # --- SQL Generators ---
    def get_alter_column_type_sql(self, table, col, new_type):
        return f"ALTER TABLE {table} ALTER COLUMN {col} TYPE {new_type};"

    def get_set_not_null_sql(self, table, col, col_type):
        return f"ALTER TABLE {table} ALTER COLUMN {col} SET NOT NULL;"

    def get_drop_column_sql(self, table, col):
        return f"ALTER TABLE {table} DROP COLUMN {col};"


class MySQLEngine(DBEngine):
    def _docker_prefix(self):
        return f"docker exec -i {self.container} " if self.is_docker else ""
    def get_base_cmd(self, db_name=None):
        target = db_name if db_name else ""
        return f"{self._docker_prefix()}mysql -h{self.host} -P{self.port} -u{self.user} -p{self.password} {target}"
    def get_admin_db_name(self): return ""
    def drop_db(self, db_name):
        run_command(f'{self.get_base_cmd()} -e "DROP DATABASE IF EXISTS {db_name};"')
    def create_db(self, db_name):
        run_command(f'{self.get_base_cmd()} -e "CREATE DATABASE {db_name};"')
    def clone_db(self, source, target):
        self.create_db(target)
        dump = f"mysqldump -h{self.host} -P{self.port} -u{self.user} -p{self.password} {source}"
        if self.is_docker: dump = f"docker exec {self.container} {dump}"
        run_command(f"{dump} | {self.get_base_cmd(target)}")

    def get_tables(self, db_name):
        cmd = f'{self.get_base_cmd(db_name)} -N -e "SHOW TABLES;"'
        out = run_command(cmd, capture=True)
        return [line.strip() for line in out.splitlines() if line.strip()]

    def inspect_db(self, db_name):
        # Improved Inspector: Captures Defaults + Length/Precision
        query = """
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT,
                   CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            ORDER BY TABLE_NAME, ORDINAL_POSITION;
        """
        cmd = f'{self.get_base_cmd(db_name)} -N -B -e "{query}"'
        out = run_command(cmd, capture=True)
        schema = {}
        if not out: return schema
        for line in out.splitlines():
            parts = line.split("\t")
            if len(parts) < 8: continue
            t_name, c_name, dtype, nullable = parts[0], parts[1], parts[2], parts[3]
            default_val = parts[4] if len(parts) > 4 else None
            char_len = parts[5] if len(parts) > 5 and parts[5] not in (None, '', 'NULL') else None
            num_prec = parts[6] if len(parts) > 6 and parts[6] not in (None, '', 'NULL') else None
            num_scale = parts[7] if len(parts) > 7 and parts[7] not in (None, '', 'NULL') else None
            
            if t_name not in schema: schema[t_name] = {}
            schema[t_name][c_name] = {
                "type": dtype,
                "length": int(char_len) if char_len else None,
                "precision": int(num_prec) if num_prec else None,
                "scale": int(num_scale) if num_scale else None,
                "nullable": nullable == "YES",
                "default": default_val
            }
        return schema

    def dump_table_create(self, db_name, table):
        dump = f"mysqldump -h{self.host} -P{self.port} -u{self.user} -p{self.password} --no-data {db_name} {table}"
        if self.is_docker: dump = f"docker exec {self.container} {dump}"
        sql = run_command(dump, capture=True)
        if sql:
            sql = sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
        return sql

    def dump_table_data(self, db_name, table):
        dump = f"mysqldump -h{self.host} -P{self.port} -u{self.user} -p{self.password} --no-create-info --complete-insert --skip-extended-insert {db_name} {table}"
        if self.is_docker: dump = f"docker exec {self.container} {dump}"
        return run_command(dump, capture=True)

    def get_primary_keys(self, db_name, table):
        query = f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table}' AND CONSTRAINT_NAME = 'PRIMARY'
            ORDER BY ORDINAL_POSITION;
        """
        cmd = f'{self.get_base_cmd(db_name)} -N -B -e "{query}"'
        out = run_command(cmd, capture=True)
        return [line.strip() for line in out.splitlines() if line.strip()]

    # --- SQL Generators ---
    def get_alter_column_type_sql(self, table, col, new_type):
        return f"ALTER TABLE {table} MODIFY COLUMN {col} {new_type};"

    def get_set_not_null_sql(self, table, col, col_type):
        # MySQL needs the full type to set NOT NULL
        return f"ALTER TABLE {table} MODIFY COLUMN {col} {col_type} NOT NULL;"

    def get_drop_column_sql(self, table, col):
        return f"ALTER TABLE {table} DROP COLUMN {col};"


# --- CORE LOGIC (PLANNER) ---

def load_config():
    if not os.path.exists(CONFIG_FILE): raise DBLError("Falta dbl.yaml. Ejecuta 'init'.")
    with open(CONFIG_FILE, 'r') as f: return yaml.safe_load(f)

def get_engine(config):
    if config['engine'] == 'postgres': return PostgresEngine(config)
    elif config['engine'] == 'mysql': return MySQLEngine(config)
    else: raise DBLError(f"Motor '{config['engine']}' no soportado.")

def get_target_db(config):
    is_sandbox = os.path.exists(SANDBOX_META_FILE)
    if is_sandbox:
        with open(SANDBOX_META_FILE) as f: meta = json.load(f)
        log(f"🛡️  Sandbox Active (Backup: {meta['backup_db']})", "warn")
    return config['db_name'], is_sandbox

def get_state(engine, db_name, config):
    """Compute current DB state for comparison."""
    log(f"Analyzing state of: {db_name}...", "info")
    
    # 1. Schema State
    try:
        schema_dict = engine.inspect_db(db_name)
        # Hash the schema AST JSON to detect structural changes
        schema_hash = hashlib.md5(json.dumps(schema_dict, sort_keys=True).encode()).hexdigest()
    except Exception as e:
        raise DBLError(f"Error inspeccionando esquema de '{db_name}': {e}")

    # 2. Data State (Tracked tables)
    whitelist = config.get('track_tables', [])
    blacklist = config.get('ignore_tables', [])
    
    # Determine which tables to read
    all_tables = set(schema_dict.keys())
    if whitelist:
        track_tables = [t for t in whitelist if t in all_tables]
    else:
        track_tables = [t for t in all_tables if t not in blacklist]
        track_tables.sort()
    
    data_hashes = {}
    for table in track_tables:
        try:
            pk_cols = engine.get_primary_keys(db_name, table)

            if not pk_cols:
                log(f"Table {table} has no PK, skipping data tracking", "warn")
                continue
                
            order_by = ', '.join(pk_cols) if pk_cols else '1'
            query = f'SELECT * FROM {table} ORDER BY {order_by}'
            cmd = f'{engine.get_base_cmd(db_name)} -c "{query}"'
            data_raw = run_command(cmd, capture=True, env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
            data_hashes[table] = hashlib.md5(data_raw.encode()).hexdigest()
        except Exception:
            data_hashes[table] = "read_error"

    return {"schema": schema_hash, "data": data_hashes}

def generate_migration_sql(config, engine, active_db, backup_db, include_data=False):
    log("🕵️  Inspecting schemas...", "info")
    active_schema = engine.inspect_db(active_db)
    backup_schema = engine.inspect_db(backup_db)

    def format_type(info):
        dt = info.get('type')
        length = info.get('length')
        prec = info.get('precision')
        scale = info.get('scale')
        if isinstance(engine, PostgresEngine):
            if dt in ('character varying', 'varchar'):
                return f"character varying({length})" if length else "character varying"
            if dt in ('numeric', 'decimal'):
                if prec and scale is not None:
                    return f"numeric({prec},{scale})"
                elif prec:
                    return f"numeric({prec})"
                else:
                    return "numeric"
            return dt
        else:
            if dt in ('varchar', 'char'):
                return f"{dt}({length})" if length else dt
            if dt in ('decimal', 'numeric'):
                if prec and scale is not None:
                    return f"{dt}({prec},{scale})"
                elif prec:
                    return f"{dt}({prec})"
                else:
                    return dt
            return dt

    policies = config.get('policies', {
        'allow_drop_table': False,
        'allow_drop_column': False
    })
    
    sql = []
    expand_sql = []       # New columns/tables
    type_changes_sql = [] # Type changes
    hardening_sql = []    # Deferred NOT NULLs (contract)
    
    sql.append(f"-- DBL Migration Layer: {datetime.now()}")
    sql.append(f"-- From: {backup_db} To: {active_db}")
    sql.append("-- ")
    sql.append("-- Phases:")
    sql.append("--   expand:   Add columns/tables (safe, no data loss)")
    sql.append("--   backfill: Update/populate data (optional)")
    sql.append("--   contract: Remove/constrain (careful, review)")
    sql.append("")

    active_tables = set(active_schema.keys())
    backup_tables = set(backup_schema.keys())

    # 1. New Tables (CREATE) - EXPAND PHASE
    new_tables = active_tables - backup_tables
    if new_tables:
        sql.append("-- [EXPAND PHASE] --")
        sql.append("-- New tables (safe, no conflicts)")
        for t in sorted(new_tables):
            sql.append(f"-- phase: expand")
            sql.append(engine.dump_table_create(active_db, t))
            sql.append("")

    # 2. Modified Tables (ALTER) - EXPAND & CONTRACT PHASES
    common_tables = active_tables & backup_tables
    for t in sorted(common_tables):
        active_cols = active_schema[t]
        backup_cols = backup_schema[t]
        
        new_col_names = set(active_cols.keys()) - set(backup_cols.keys())
        dropped_col_names = set(backup_cols.keys()) - set(active_cols.keys())
        common_col_names = set(active_cols.keys()) & set(backup_cols.keys())
        
        # 2.1 New Columns - EXPAND PHASE
        if new_col_names:
            sql.append(f"-- [EXPAND in {t}] --")
            for col in sorted(new_col_names):
                ctype = format_type(active_cols[col])
                sql.append(f"-- phase: expand")
                sql.append(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS {col} {ctype};")
                
                # Detect NOT NULL intention for contract phase
                if not active_cols[col]['nullable']:
                    hardening_sql.append(f"-- [phase: contract] Make {t}.{col} NOT NULL")
                    hardening_sql.append(f"-- {engine.get_set_not_null_sql(t, col, ctype)}")

        # 2.2 Type Changes - REVIEW CAREFULLY
        for col in common_col_names:
            active_sig = format_type(active_cols[col])
            backup_sig = format_type(backup_cols[col])
            if active_sig != backup_sig:
                type_changes_sql.append(f"-- phase: contract (risky type change)")
                type_changes_sql.append(f"-- [TYPE CHANGE] {t}.{col}: {backup_sig} -> {active_sig}")
                type_changes_sql.append(f"-- {engine.get_alter_column_type_sql(t, col, active_sig)}")

        # 2.3 Dropped Columns - CONTRACT PHASE (SAFE)
        if dropped_col_names:
            sql.append(f"-- [CONTRACT in {t}] --")
            for col in sorted(dropped_col_names):
                sql.append(f"-- phase: contract (dangerous, review)")
                sql.append(f"-- [DANGEROUS] Dropped column: {col}")
                sql.append(f"-- {engine.get_drop_column_sql(t, col)}")

    # 2.4 Insert grouped type changes
    if type_changes_sql:
        sql.append("")
        sql.append("-- [TYPE CHANGES - REVIEW CAREFULLY] --")
        sql.extend(type_changes_sql)
        sql.append("")

    sql.append("")

    # 3. Dropped Tables - CONTRACT PHASE (VERY DANGEROUS)
    dropped_tables = backup_tables - active_tables
    if dropped_tables:
        sql.append("-- [CONTRACT PHASE - DROPPED TABLES] --")
        for t in sorted(dropped_tables):
            sql.append(f"-- phase: contract (very dangerous)")
            sql.append(f"-- [DANGEROUS] Table dropped in active DB: {t}")
            sql.append(f"-- DROP TABLE IF EXISTS {t};")
        sql.append("")
    
    # 4. Hardening Phase - CONTRACT PHASE (Delayed Constraints)
    if hardening_sql:
        sql.append("-- [CONTRACT PHASE - HARDENING / CONSTRAINTS] --")
        sql.append("-- These are deferred constraints. Uncomment after verifying data.")
        sql.extend(hardening_sql)
        sql.append("")

    # 5. Data Sync - ONLY IF EXPLICITLY REQUESTED
    if include_data:
        whitelist = config.get('track_tables', [])
        blacklist = config.get('ignore_tables', [])
        data_sql_buffer = []
        
        # Detect data hash changes
        candidates = [t for t in common_tables if (t in whitelist) or (not whitelist and t not in blacklist)]
        if candidates:
            current_state = get_state(engine, active_db, config)
            backup_state = get_state(engine, backup_db, config)
            
            for t in sorted(candidates):
                if current_state['data'].get(t) != backup_state['data'].get(t):
                    data_sql_buffer.append(f"-- phase: backfill (data-only, optional)")
                    data_sql_buffer.append(f"-- Data changed in: {t}")
                    data_sql_buffer.append(f"TRUNCATE TABLE {t};")
                    data_sql_buffer.append(engine.dump_table_data(active_db, t))
                    data_sql_buffer.append("")
            
            if data_sql_buffer:
                sql.append("")
                sql.append("-- [BACKFILL PHASE - DATA SYNC] --")
                sql.append("-- ⚠️  Data operations are destructive (TRUNCATE).")
                sql.append("-- Ensure these are lookup/reference tables only.")
                sql.extend(data_sql_buffer)
    else:
        # Warn if data changes detected but not included
        whitelist = config.get('track_tables', [])
        blacklist = config.get('ignore_tables', [])
        candidates = [t for t in common_tables if (t in whitelist) or (not whitelist and t not in blacklist)]
        if candidates:
            current_state = get_state(engine, active_db, config)
            backup_state = get_state(engine, backup_db, config)
            data_changed = [t for t in sorted(candidates) if current_state['data'].get(t) != backup_state['data'].get(t)]
            
            if data_changed:
                sql.append("")
                sql.append("-- [⚠️  DATA CHANGES DETECTED] --")
                sql.append("-- The following tables have changed data:")
                for t in data_changed:
                    sql.append(f"--   {t}")
                sql.append("-- To include data sync, use: dbl commit -m \"msg\" --with-data")
                sql.append("")

    return "\n".join(sql)

# --- COMANDOS ---

def cmd_init(args):
    if os.path.exists(CONFIG_FILE): return log("dbl.yaml already exists", "warn")
    os.makedirs(LAYERS_DIR, exist_ok=True)
    config = {
        "engine": "postgres", "container_name": "", "host": "localhost", "port": 5432,
        "db_name": "myapp", "user": "postgres", "password": "password",
        "ignore_tables": ["migrations", "failed_jobs", "sessions"], "policies": { "allow_drop_table": False, "allow_drop_column": False  }
    }
    with open(CONFIG_FILE, 'w') as f: yaml.dump(config, f)
    save_manifest({"current": "master", "branches": {"master": []}})
    log(f"Created {CONFIG_FILE}. Initial branch: master", "success")
    log(f"Please review and adjust configuration before proceeding.", "info")

def cmd_import(args):
    config = load_config()
    engine = get_engine(config)
    db = config['db_name']
    if not confirm_action(f"This will import the snapshot and recreate database '{db}'. Continue?"):
        return
    run_command(f"cp {args.file} {SNAPSHOT_FILE}")
    engine.drop_db(db); engine.create_db(db)
    run_command(f"cat {SNAPSHOT_FILE} | {engine.get_base_cmd(db)}", env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
    save_manifest({"current": "master", "branches": {"master": []}})
    log("Snapshot imported. Master reset.", "success")

def cmd_sandbox(args):
    config = load_config()
    engine = get_engine(config)
    db = config['db_name']
    
    if args.action == "start":
        if os.path.exists(SANDBOX_META_FILE): return log("Sandbox already active.", "error")
        bk = f"{db}_dbl_shadow_{int(time.time())}"
        log("🛡️  Creating safe environment (Sandbox)...", "header")
        engine.backup_db(db, bk)
        with open(SANDBOX_META_FILE, 'w') as f:
            json.dump({"mode":"shadow","active_db":db,"backup_db":bk}, f)
        log("✅ Sandbox ready. You can work locally as usual.", "success")
        
    elif args.action == "rollback":
        if not os.path.exists(SANDBOX_META_FILE): return log("No sandbox active.", "error")
        with open(SANDBOX_META_FILE) as f: meta = json.load(f)
        log("🔙 Reverting changes...", "warn")
        engine.drop_db(meta['active_db'])
        engine.clone_db(meta['backup_db'], meta['active_db'])
        engine.drop_db(meta['backup_db'])
        os.remove(SANDBOX_META_FILE)
        log("DB restored to original state.", "success")
        
    elif args.action == "apply":
        if not os.path.exists(SANDBOX_META_FILE): return log("No sandbox active.", "error")

        with open(SANDBOX_META_FILE) as f: meta = json.load(f)
        log("💾 Confirming changes (Sandbox closed)...", "success")
        engine.drop_db(meta['backup_db'])
        os.remove(SANDBOX_META_FILE)

    elif args.action == "status":
        if os.path.exists(SANDBOX_META_FILE):
            with open(SANDBOX_META_FILE) as f: meta = json.load(f)
            log(f"Sandbox Active: {meta['active_db']} (Shadow: {meta['backup_db']})", "branch")
        else:
            m = load_manifest()
            log(f"Current branch: {m['current']}", "info")

def cmd_diff(args):
    config = load_config()
    engine = get_engine(config)
    target_db, is_sandbox = get_target_db(config)
    
    current_state = get_state(engine, target_db, config)
    if not os.path.exists(STATE_FILE): return False, []
    
    if is_sandbox:
        with open(SANDBOX_META_FILE) as f: meta = json.load(f)
        baseline_state = get_state(engine, meta['backup_db'], config)
    else:
        with open(STATE_FILE) as f: baseline_state = json.load(f)

    has_changes = False
    changed_data_tables = []
    
    if current_state['schema'] != baseline_state['schema']:
        log("🔴 SCHEMA CHANGE detected", "warn")
        has_changes = True
    
    for table, h in current_state['data'].items():
        if h != baseline_state['data'].get(table):
            log(f"🔴 DATA CHANGE: {table}", "warn")
            has_changes = True
            changed_data_tables.append(table)
            
    if not has_changes: log(f"🟢 All clean in {target_db}", "success")
    # return has_changes, changed_data_tables
    sys.exit(0 if not has_changes else 1)

def cmd_commit(args):
    config = load_config()
    engine = get_engine(config)
    db, is_sandbox = get_target_db(config)
    
    if not is_sandbox: return log("You must be in sandbox: dbl sandbox start", "error")
    
    with open(SANDBOX_META_FILE) as f: meta = json.load(f)
    backup_db = meta['backup_db']
    
    # Check if user wants to include data sync
    include_data = args.with_data if hasattr(args, 'with_data') and args.with_data else False
    
    # Core planner (with phase metadata)
    sql = generate_migration_sql(config, engine, db, backup_db, include_data=include_data)
    
    # Check if there is actual SQL (not only comments)
    clean_lines = [l for l in sql.splitlines() if not l.strip().startswith("--") and l.strip()]
    if not clean_lines:
        return log("No structural or data changes detected.", "warn")
    
    # Editor
    with tempfile.NamedTemporaryFile(suffix=".sql", mode='w+', delete=False) as tf:
        tf.write(sql)
        tpath = tf.name
    
    editor = os.environ.get('EDITOR', 'nano')
    try: subprocess.call([editor, tpath])
    except: pass
    
    with open(tpath, 'r') as f: final_sql = f.read().strip()
    os.remove(tpath)
    
    if not final_sql or len([l for l in final_sql.splitlines() if not l.strip().startswith("--")]) == 0:
        return log("Commit canceled (empty SQL).", "warn")
        
    # Guardar
    manifest = load_manifest()
    curr = manifest['current']
    fname = f"{curr}_{int(time.time())}.sql"
    
    with open(os.path.join(LAYERS_DIR, fname), 'w') as f:
        f.write(f"-- {args.message}\n{final_sql}")
    
    # Add commit metadata (non-imposing)
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

def cmd_branch(args):
    m = load_manifest()
    if args.delete:
        if args.delete == m['current']: return log("You cannot delete the current branch", "error")
        if args.delete in m['branches']: 
            del m['branches'][args.delete]
            save_manifest(m)
            log(f"Branch {args.delete} deleted", "success")
    elif args.name:
        if args.name in m['branches']: return log("Branch already exists", "error")
        # Create new branch from current (with parent tracking for future rebase)
        m['branches'][args.name] = list(m['branches'][m['current']])
        # Optional metadata: store parent for future rebase
        if '_metadata' not in m:
            m['_metadata'] = {}
        m['_metadata'][args.name] = {"parent": m['current'], "created_at": datetime.now().isoformat()}
        save_manifest(m)
        log(f"Branch {args.name} created (parent: {m['current']})", "success")
    else:
        for b in m['branches']:
            parent = ""
            if '_metadata' in m and b in m['_metadata']:
                parent = f" <- {m['_metadata'][b]['parent']}"
            log(f"{'*' if b == m['current'] else ' '} {b}{parent}", "branch")

def cmd_checkout(args):
    """Switch branch and rebuild DB."""
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

    # 2. Actualizar puntero
    manifest['current'] = target_branch
    save_manifest(manifest)
    log(f"Switching to branch '{target_branch}'...", "branch")
    
    # 3. Rebuild DB with the new branch history
    cmd_reset(args) 

def cmd_reset(args):
    config = load_config()
    engine = get_engine(config)
    db, is_sandbox = get_target_db(config)
    m = load_manifest()
    
    if not is_sandbox:
        if not confirm_action(f"This will rebuild database '{db}'. Continue?"):
            return
    
    log(f"Rebuilding {db} on branch {m['current']}...", "warn")
    engine.drop_db(db); engine.create_db(db)
    
    if os.path.exists(SNAPSHOT_FILE):
        run_command(f"cat {SNAPSHOT_FILE} | {engine.get_base_cmd(db)}", env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
        
    for l in m['branches'][m['current']]:
        path = os.path.join(LAYERS_DIR, l['file'])
        run_command(f"cat {path} | {engine.get_base_cmd(db)}", env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
    
    log("State restored.", "success")

def cmd_pull(args):
    """Pull changes from another branch without destroying it (git-like)."""
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
    
    # Get new layers from source branch
    curr_files = {l['file'] for l in m['branches'][curr]}
    new_layers = [l for l in m['branches'][src] if l['file'] not in curr_files]
    
    if not new_layers:
        return log(f"No new changes from '{src}'", "info")
    
    log(f"Pulling {len(new_layers)} layers from branch '{src}'...", "info")
    for l in new_layers:
        log(f"  Applying: {l['file']}", "info")
        path = os.path.join(LAYERS_DIR, l['file'])
        run_command(f"cat {path} | {engine.get_base_cmd(db)}", env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
        m['branches'][curr].append(l)
    
    save_manifest(m)
    log(f"Pull from '{src}' completed. Branch '{curr}' updated.", "success")

def cmd_rev_parse(args):
    """Resolve references (HEAD, current branch, hashes, etc)."""
    m = load_manifest()
    ref = args.ref.lower() if hasattr(args, 'ref') else 'head'
    
    if ref == 'head':
        # Print current branch as ref
        print(m['current'])
    else:
        # Resolve as branch
        if ref in m['branches']:
            print(f"{ref}")
        else:
            log(f"Reference '{ref}' not found", "error")

def cmd_log(args):
    """Show layer (commit) history for current or specified branch."""
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
            # Short format: hash ... message
            layer_hash = hashlib.md5(layer['file'].encode()).hexdigest()[:7]
            print(f"{layer_hash} {layer['msg']}")
        else:
            # Detailed format
            log(f"Layer: {layer['file']}", "branch")
            log(f"  Message: {layer['msg']}", "info")

def cmd_merge(args):
    m = load_manifest()
    curr, tgt = m['current'], args.branch
    if tgt not in m['branches']: return log("Target branch does not exist", "error")
    
    curr_files = {l['file'] for l in m['branches'][curr]}
    new_layers = [l for l in m['branches'][tgt] if l['file'] not in curr_files]
    
    if not new_layers: return log("Nothing to merge.", "info")
    
    config = load_config()
    engine = get_engine(config)
    db = config['db_name']
    
    for l in new_layers:
        log(f"Applying {l['file']}", "info")
        path = os.path.join(LAYERS_DIR, l['file'])
        run_command(f"cat {path} | {engine.get_base_cmd(db)}", env=engine._auth_env() if isinstance(engine, PostgresEngine) else None)
        m['branches'][curr].append(l)
    
    save_manifest(m)
    log("Merge completed.", "success")

def cmd_validate(args):
    """Validate phases without blocking (warnings only by default)."""
    # Read optional configuration
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
    
    # 1. Analyze each layer
    phases_seen = {}  # track: last layer index for each phase
    has_uncommented_drop = False
    has_mixed_data_schema = False
    
    for i, layer in enumerate(layers):
        layer_path = os.path.join(LAYERS_DIR, layer['file'])
        
        try:
            with open(layer_path, 'r') as f:
                content = f.read()
        except:
            warnings.append(f"⚠️  Could not read: {layer['file']}")
            continue
        
        lines = content.splitlines()
        
        # Detect phases in this layer
        layer_phases = set()
        has_set_not_null = False
        has_drop = False
        has_uncommented_drop_here = False
        has_backfill = False
        has_data_sync = False
        has_type_change = False
        
        for line in lines:
            stripped = line.strip()
            
            if "-- phase: expand" in stripped:
                layer_phases.add('expand')
            elif "-- phase: backfill" in stripped:
                layer_phases.add('backfill')
                has_backfill = True
            elif "-- phase: contract" in stripped:
                layer_phases.add('contract')
            
            # Detect risky operations
            if "SET NOT NULL" in stripped and not stripped.startswith("--"):
                has_set_not_null = True
            
            if "DROP TABLE" in stripped or "DROP COLUMN" in stripped:
                has_drop = True
                if not stripped.startswith("--"):
                    has_uncommented_drop_here = True
            
            # Detect TRUNCATE (indicator of data sync)
            if "TRUNCATE TABLE" in stripped and not stripped.startswith("--"):
                has_data_sync = True

            # Detect column type changes
            if detect_type_changes:
                if ("ALTER TABLE" in stripped and "ALTER COLUMN" in stripped and (" TYPE " in stripped or " SET DATA TYPE " in stripped)) and not stripped.startswith("--"):
                    has_type_change = True
                # MySQL: MODIFY COLUMN type change
                if ("ALTER TABLE" in stripped and " MODIFY " in stripped) and not stripped.startswith("--"):
                    has_type_change = True
        
        # 2. Validation: CONTRACT without prior BACKFILL
        if 'contract' in layer_phases and 'backfill' not in layer_phases:
            # Verificar si hubo backfill en capas anteriores
            had_backfill_before = 'backfill' in phases_seen
            if not had_backfill_before and 'backfill' not in layer_phases:
                msg = f"Layer {layer['file']}: Contract without prior backfill"
                (errors if strict else warnings).append(f"⚠️  {msg}" if not strict else f"❌ {msg}")

        # 2b. Validation: BACKFILL without prior EXPAND (per configuration)
        if 'backfill' in layer_phases:
            had_expand_before = 'expand' in phases_seen
            if not had_expand_before and not allow_orphaned:
                warnings.append(f"⚠️  Layer {layer['file']}: Backfill without prior expand (config: allow_orphaned=false)")
        
        # 3. Validation: uncommented DROP
        if has_uncommented_drop_here:
            msg = f"Layer {layer['file']}: DROP not commented (will execute immediately)"
            (errors if strict and require_comments else warnings).append(f"⚠️  {msg}" if not (strict and require_comments) else f"❌ {msg}")
        elif require_comments and has_drop and 'contract' not in layer_phases:
            warnings.append(f"⚠️  Layer {layer['file']}: Contract operation without 'phase: contract' comment")
            has_uncommented_drop = True
        
        # 4. Validation: SET NOT NULL without default/backfill
        if has_set_not_null:
            # Check if there is a prior UPDATE/INSERT to populate data
            has_data_op_before = False
            for prev_line in lines:
                if "UPDATE" in prev_line and not prev_line.strip().startswith("--"):
                    has_data_op_before = True
                if "INSERT INTO" in prev_line and not prev_line.strip().startswith("--"):
                    has_data_op_before = True
            
            if not has_data_op_before:
                msg = f"Layer {layer['file']}: SET NOT NULL without prior UPDATE/INSERT to populate data"
                (errors if strict else warnings).append(f"⚠️  {msg}" if not strict else f"❌ {msg}")
        
        # 5. Validation: Data + Schema mixed in same layer
        if has_data_sync:
            if 'expand' in layer_phases or 'contract' in layer_phases:
                has_mixed_data_schema = True
            warnings.append(f"⚠️  Layer {layer['file']}: TRUNCATE + ALTER TABLE (data + schema mixed)")
        
        # 6. Validation: Inconsistent commit type
        layer_type = layer.get('type', 'unknown')
        if has_data_sync and layer_type == 'schema':
            warnings.append(f"⚠️  Layer {layer['file']}: Has TRUNCATE but marked as 'schema' (should be 'schema+data')")

        # 7. Validation: Type changes
        if detect_type_changes and has_type_change:
            warnings.append(f"⚠️  Layer {layer['file']}: Column type change detected (review compatibility)")
        
        # Update phases_seen
        phases_seen.update({p: i for p in layer_phases})
    
    # 3. Result
    if hasattr(args, 'fix') and args.fix:
        log("🔧 Autofix not implemented (planned for v0.5)", "warn")
        log("   Tip: use backup branches and reorder phases manually.", "info")
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

def cmd_rebase(args):
    """Rebase current branch onto another (git-style)."""
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

def cmd_version(args):
    """Show version information."""
    log(f"DBL (Database Layering) v{VERSION}", "header")
    log("Repository: https://github.com/alann-estrada-KSH/dbl-sandbox", "info")

def cmd_help(args):
    log("Available commands:", "info")
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

# --- MAIN ---
def main():
    parser = CustomParser(description="DBL - Database Layering")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    sub.add_parser("help")
    sub.add_parser("version")
    sub.add_parser("init")
    sub.add_parser("import").add_argument("file")
    
    sb = sub.add_parser("sandbox")
    sb_act = sb.add_subparsers(dest="action", required=True)
    sb_act.add_parser("start")
    sb_act.add_parser("rollback")
    sb_act.add_parser("apply")
    sb_act.add_parser("status")
    
    sub.add_parser("diff")
    com_p = sub.add_parser("commit")
    com_p.add_argument("-m", "--message", required=True)
    com_p.add_argument("--with-data", action="store_true", help="Include data sync (opt-in)")
    
    br = sub.add_parser("branch")
    br.add_argument("name", nargs="?", help="New branch name")
    br.add_argument("-d", "--delete", help="Branch name to delete")
    
    sub.add_parser("checkout").add_argument("branch", help="Branch name to switch to")
    sub.add_parser("merge").add_argument("branch", help="Branch name to merge")
    sub.add_parser("pull").add_argument("branch", help="Branch name to pull from")
    # Rebase options
    re_p = sub.add_parser("rebase", help="Rebase current branch")
    re_p.add_argument("onto", help="Target base branch")
    re_p.add_argument("--dry-run", action="store_true", help="Show result without applying")
    re_p.add_argument("--no-backup", action="store_true", help="Do not create backup branch before rebase")
    
    log_p = sub.add_parser("log", help="View layer history")
    log_p.add_argument("branch", nargs="?", help="Branch to view (default: current)")
    log_p.add_argument("--oneline", action="store_true", help="Short format")
    log_p.add_argument("-n", type=int, help="Number of layers to show")
    
    rev_p = sub.add_parser("rev-parse", help="Resolve references")
    rev_p.add_argument("ref", help="Reference to resolve (HEAD, branch, etc)")
    
    sub.add_parser("reset")

    val = sub.add_parser("validate", help="Validate anomalies in layers")
    val.add_argument("branch", nargs="?", help="Branch to validate (optional, uses current)")
    val.add_argument("--fix", action="store_true", help="(Future) Attempt safe autofix")

    try:
        args = parser.parse_args()
        
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
        elif args.cmd == "help": cmd_help(args)
        else: cmd_help(args)

    except InvalidCommandError: log("Invalid command. Type 'dbl help' to see available commands.", "error")
    except DBLError as e: log(str(e), "error")
    except KeyboardInterrupt: print("\n")
    except Exception as e: log(f"Error inesperado: {e}", "error")

if __name__ == "__main__": main()
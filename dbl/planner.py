"""Migration SQL generation (planner)"""

from datetime import datetime
from .engines.postgres import PostgresEngine
from .state import get_state
from .utils import log


def generate_migration_sql(config, engine, active_db, backup_db, include_data=False):
    """Generate migration SQL by comparing two database states"""
    log("🕵️  Inspecting schemas...", "info")
    active_schema = engine.inspect_db(active_db)
    backup_schema = engine.inspect_db(backup_db)

    def format_type(info):
        """Format column type with length/precision"""
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
    type_changes_sql = []
    hardening_sql = []
    
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

    # 1. New Tables (EXPAND)
    new_tables = active_tables - backup_tables
    if new_tables:
        sql.append("-- [EXPAND PHASE] --")
        sql.append("-- New tables (safe, no conflicts)")
        for t in sorted(new_tables):
            sql.append(f"-- phase: expand")
            sql.append(engine.dump_table_create(active_db, t))
            sql.append("")

    # 2. Modified Tables
    common_tables = active_tables & backup_tables
    for t in sorted(common_tables):
        active_cols = active_schema[t]
        backup_cols = backup_schema[t]
        
        new_col_names = set(active_cols.keys()) - set(backup_cols.keys())
        dropped_col_names = set(backup_cols.keys()) - set(active_cols.keys())
        common_col_names = set(active_cols.keys()) & set(backup_cols.keys())
        
        # New Columns (EXPAND)
        if new_col_names:
            sql.append(f"-- [EXPAND in {t}] --")
            for col in sorted(new_col_names):
                ctype = format_type(active_cols[col])
                sql.append(f"-- phase: expand")
                sql.append(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS {col} {ctype};")
                
                if not active_cols[col]['nullable']:
                    hardening_sql.append(f"-- [phase: contract] Make {t}.{col} NOT NULL")
                    hardening_sql.append(f"-- {engine.get_set_not_null_sql(t, col, ctype)}")

        # Type Changes
        for col in common_col_names:
            active_sig = format_type(active_cols[col])
            backup_sig = format_type(backup_cols[col])
            if active_sig != backup_sig:
                type_changes_sql.append(f"-- phase: contract (risky type change)")
                type_changes_sql.append(f"-- [TYPE CHANGE] {t}.{col}: {backup_sig} -> {active_sig}")
                type_changes_sql.append(f"-- {engine.get_alter_column_type_sql(t, col, active_sig)}")

        # Dropped Columns (CONTRACT)
        if dropped_col_names:
            sql.append(f"-- [CONTRACT in {t}] --")
            for col in sorted(dropped_col_names):
                sql.append(f"-- phase: contract (dangerous, review)")
                sql.append(f"-- [DANGEROUS] Dropped column: {col}")
                sql.append(f"-- {engine.get_drop_column_sql(t, col)}")

    if type_changes_sql:
        sql.append("")
        sql.append("-- [TYPE CHANGES - REVIEW CAREFULLY] --")
        sql.extend(type_changes_sql)
        sql.append("")

    sql.append("")

    # 3. Dropped Tables (CONTRACT)
    dropped_tables = backup_tables - active_tables
    if dropped_tables:
        sql.append("-- [CONTRACT PHASE - DROPPED TABLES] --")
        for t in sorted(dropped_tables):
            sql.append(f"-- phase: contract (very dangerous)")
            sql.append(f"-- [DANGEROUS] Table dropped in active DB: {t}")
            sql.append(f"-- DROP TABLE IF EXISTS {t};")
        sql.append("")
    
    # 4. Hardening (CONTRACT)
    if hardening_sql:
        sql.append("-- [CONTRACT PHASE - HARDENING / CONSTRAINTS] --")
        sql.append("-- These are deferred constraints. Uncomment after verifying data.")
        sql.extend(hardening_sql)
        sql.append("")

    # 5. Data Sync (BACKFILL)
    if include_data:
        whitelist = config.get('track_tables', [])
        blacklist = config.get('ignore_tables', [])
        data_sql_buffer = []
        
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

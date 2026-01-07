"""PostgreSQL engine implementation"""

import os
from .base import DBEngine
from ..utils import run_command, log


class PostgresEngine(DBEngine):
    """PostgreSQL database engine implementation"""
    
    def _docker_prefix(self):
        return f"docker exec {self.container} " if self.is_docker else ""
    
    def _auth_env(self):
        env = os.environ.copy()
        if not self.is_docker: 
            env['PGPASSWORD'] = self.password
        return env
    
    def get_base_cmd(self, db_name=None):
        target = db_name if db_name else "postgres"
        cmd = f"psql -h {self.host} -p {self.port} -U {self.user} -d {target} -v ON_ERROR_STOP=1"
        return self._docker_prefix() + cmd
    
    def get_admin_db_name(self): 
        return "postgres"

    def drop_db(self, db_name):
        kill = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db_name}' AND pid <> pg_backend_pid();"
        run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "{kill}"', env=self._auth_env())
        run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "DROP DATABASE IF EXISTS {db_name};"', env=self._auth_env())
    
    def create_db(self, db_name):
        run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "CREATE DATABASE {db_name};"', env=self._auth_env())

    def clone_db(self, source, target):
        log(f"   🔄 Cloning {source} → {target}...", "info")
        
        import subprocess, threading, sys
        # Show spinner
        stop_spinner = False
        def spinner():
            chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            idx = 0
            while not stop_spinner:
                sys.stdout.write(f'\r   {chars[idx % len(chars)]} Cloning database...')
                sys.stdout.flush()
                idx += 1
                threading.Event().wait(0.1)
            sys.stdout.write('\r   ✓ Database cloned successfully' + ' '*20 + '\n')
            sys.stdout.flush()
        
        t = threading.Thread(target=spinner)
        t.start()
        try:
            kill = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{source}' AND pid <> pg_backend_pid();"
            run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "{kill}"', env=self._auth_env())
            run_command(f'{self.get_base_cmd(self.get_admin_db_name())} -c "CREATE DATABASE {target} WITH TEMPLATE {source};"', env=self._auth_env())
        except Exception:
            log("Fallback a pg_dump (Clone lento)...", "warn")
            self.create_db(target)
            dump = f"pg_dump -h {self.host} -p {self.port} -U {self.user} {source}"
            if self.is_docker: 
                dump = f"docker exec {self.container} {dump}"
            run_command(f"{dump} | {self.get_base_cmd(target)}", env=self._auth_env())
        finally:
            stop_spinner = True
            t.join()

    def get_tables(self, db_name):
        cmd = f'{self.get_base_cmd(db_name)} -t -c "SELECT tablename FROM pg_tables WHERE schemaname=\'public\';"'
        out = run_command(cmd, capture=True, env=self._auth_env())
        return [line.strip() for line in out.splitlines() if line.strip()]
    
    def execute_query(self, db_name, query):
        """Execute a query and return command string for PostgreSQL"""
        return f'{self.get_base_cmd(db_name)} -t -A -c "{query}"'

    def inspect_db(self, db_name):
        query = "SELECT table_name, column_name, data_type, is_nullable, column_default, character_maximum_length, numeric_precision, numeric_scale FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position;"
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
            
            if t_name not in schema: 
                schema[t_name] = {}
            
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
        if self.is_docker: 
            dump = f"docker exec {self.container} {dump}"
        sql = run_command(dump, capture=True, env=self._auth_env())
        if sql:
            sql = sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
        return sql

    def dump_table_data(self, db_name, table):
        dump = f"pg_dump -h {self.host} -p {self.port} -U {self.user} --data-only --column-inserts --table=public.{table} {db_name}"
        if self.is_docker: 
            dump = f"docker exec {self.container} {dump}"
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

    def get_alter_column_type_sql(self, table, col, new_type):
        return f"ALTER TABLE {table} ALTER COLUMN {col} TYPE {new_type};"

    def get_set_not_null_sql(self, table, col, col_type):
        return f"ALTER TABLE {table} ALTER COLUMN {col} SET NOT NULL;"

    def get_drop_column_sql(self, table, col):
        return f"ALTER TABLE {table} DROP COLUMN {col};"

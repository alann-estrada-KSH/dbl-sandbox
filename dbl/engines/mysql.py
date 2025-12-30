"""MySQL engine implementation"""

from .base import DBEngine
from ..utils import run_command


class MySQLEngine(DBEngine):
    """MySQL database engine implementation"""
    
    def _docker_prefix(self):
        return f"docker exec -i {self.container} " if self.is_docker else ""
    
    def get_base_cmd(self, db_name=None):
        target = db_name if db_name else ""
        return f"{self._docker_prefix()}mysql -h{self.host} -P{self.port} -u{self.user} -p{self.password} {target}"
    
    def get_admin_db_name(self): 
        return ""
    
    def drop_db(self, db_name):
        run_command(f'{self.get_base_cmd()} -e "DROP DATABASE IF EXISTS {db_name};"')
    
    def create_db(self, db_name):
        run_command(f'{self.get_base_cmd()} -e "CREATE DATABASE {db_name};"')
    
    def clone_db(self, source, target):
        self.create_db(target)
        dump = f"mysqldump -h{self.host} -P{self.port} -u{self.user} -p{self.password} {source}"
        if self.is_docker: 
            dump = f"docker exec {self.container} {dump}"
        run_command(f"{dump} | {self.get_base_cmd(target)}")

    def get_tables(self, db_name):
        cmd = f'{self.get_base_cmd(db_name)} -N -e "SHOW TABLES;"'
        out = run_command(cmd, capture=True)
        return [line.strip() for line in out.splitlines() if line.strip()]

    def inspect_db(self, db_name):
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
        dump = f"mysqldump -h{self.host} -P{self.port} -u{self.user} -p{self.password} --no-data {db_name} {table}"
        if self.is_docker: 
            dump = f"docker exec {self.container} {dump}"
        sql = run_command(dump, capture=True)
        if sql:
            sql = sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
        return sql

    def dump_table_data(self, db_name, table):
        dump = f"mysqldump -h{self.host} -P{self.port} -u{self.user} -p{self.password} --no-create-info --complete-insert --skip-extended-insert {db_name} {table}"
        if self.is_docker: 
            dump = f"docker exec {self.container} {dump}"
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

    def get_alter_column_type_sql(self, table, col, new_type):
        return f"ALTER TABLE {table} MODIFY COLUMN {col} {new_type};"

    def get_set_not_null_sql(self, table, col, col_type):
        return f"ALTER TABLE {table} MODIFY COLUMN {col} {col_type} NOT NULL;"

    def get_drop_column_sql(self, table, col):
        return f"ALTER TABLE {table} DROP COLUMN {col};"

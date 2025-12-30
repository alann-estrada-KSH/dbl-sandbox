"""Abstract base class for database engines"""

from abc import ABC, abstractmethod


class DBEngine(ABC):
    """Base class for database engine implementations"""
    
    def __init__(self, config):
        self.host = config.get('host', 'localhost')
        self.port = str(config.get('port', '5432'))
        self.user = config.get('user', 'postgres')
        self.password = config.get('password', '')
        self.container = config.get('container_name')
        self.is_docker = bool(self.container)

    @abstractmethod
    def get_base_cmd(self, db_name=None):
        """Get base command for database CLI"""
        pass
    
    @abstractmethod
    def get_admin_db_name(self):
        """Get the admin database name"""
        pass
    
    @abstractmethod
    def drop_db(self, db_name):
        """Drop a database"""
        pass
    
    @abstractmethod
    def create_db(self, db_name):
        """Create a database"""
        pass
    
    @abstractmethod
    def clone_db(self, source_db, target_db):
        """Clone a database"""
        pass
    
    @abstractmethod
    def get_tables(self, db_name):
        """Get list of tables in database"""
        pass
    
    # --- INSPECTOR (AST Generator) ---
    @abstractmethod
    def inspect_db(self, db_name):
        """Inspect database schema and return AST"""
        pass
    
    @abstractmethod
    def dump_table_create(self, db_name, table):
        """Dump CREATE TABLE statement"""
        pass
    
    @abstractmethod
    def dump_table_data(self, db_name, table):
        """Dump table data as INSERT statements"""
        pass
    
    # --- SQL GENERATORS (Dialect Specific) ---
    @abstractmethod
    def get_alter_column_type_sql(self, table, col, new_type):
        """Generate SQL to alter column type"""
        pass
    
    @abstractmethod
    def get_set_not_null_sql(self, table, col, col_type):
        """Generate SQL to set column NOT NULL"""
        pass
    
    @abstractmethod
    def get_drop_column_sql(self, table, col):
        """Generate SQL to drop column"""
        pass
    
    @abstractmethod
    def get_primary_keys(self, db_name, table):
        """Get primary key columns for a table"""
        pass

    def backup_db(self, source_db, backup_db):
        """Backup a database by cloning it"""
        self.clone_db(source_db, backup_db)

"""Configuration management"""

import os
import yaml
from .constants import CONFIG_FILE
from .errors import DBLError
from .engines import PostgresEngine, MySQLEngine


def load_config():
    """Load configuration from dbl.yaml"""
    if not os.path.exists(CONFIG_FILE): 
        raise DBLError("Falta dbl.yaml. Ejecuta 'init'.")
    with open(CONFIG_FILE, 'r') as f: 
        return yaml.safe_load(f)


def get_engine(config):
    """Get database engine instance based on configuration"""
    if config['engine'] == 'postgres': 
        return PostgresEngine(config)
    elif config['engine'] == 'mysql': 
        return MySQLEngine(config)
    else: 
        raise DBLError(f"Motor '{config['engine']}' no soportado.")

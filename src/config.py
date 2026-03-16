"""
Configuration Module
====================
This file stores all configuration settings in one place.
This makes it easy to change settings without modifying the actual code.

IMPORTANT: 
- Copy .env.example to .env and add your MySQL password
- Never commit .env to GitHub (it contains your password!)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This keeps passwords out of the code!
load_dotenv()


# ============================================================
# DATABASE CONFIGURATION
# ============================================================
# These settings tell Python how to connect to MySQL

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),      # MySQL server address
    'port': int(os.getenv('DB_PORT', '3306')),      # MySQL port (default: 3306)
    'database': os.getenv('DB_NAME', 'sales_dwh'),  # Database name
    'user': os.getenv('DB_USER', 'root'),           # MySQL username
    'password': os.getenv('DB_PASSWORD', ''),       # MySQL password (from .env)
}


# ============================================================
# FILE PATHS
# ============================================================
# Where to find and save data files

import os

# Get the project root directory (parent of src folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directories
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
SAMPLE_DATA_DIR = os.path.join(DATA_DIR, 'sample')

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLE_DATA_DIR]:
    os.makedirs(directory, exist_ok=True)


# ============================================================
# ETL SETTINGS
# ============================================================

# How many rows to insert at once (for performance)
BATCH_SIZE = int(os.getenv('ETL_BATCH_SIZE', '1000'))

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


# ============================================================
# HELPER FUNCTION: Print configuration (for debugging)
# ============================================================

def print_config():
    """Print current configuration (hide password)"""
    print("=" * 50)
    print("CURRENT CONFIGURATION")
    print("=" * 50)
    print(f"Database Host: {DB_CONFIG['host']}")
    print(f"Database Port: {DB_CONFIG['port']}")
    print(f"Database Name: {DB_CONFIG['database']}")
    print(f"Database User: {DB_CONFIG['user']}")
    print(f"Database Password: {'*' * len(DB_CONFIG['password']) if DB_CONFIG['password'] else '(not set)'}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print("=" * 50)


# Run this to test configuration
if __name__ == "__main__":
    print_config()

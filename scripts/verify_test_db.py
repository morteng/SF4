import os
import sys
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def verify_test_db(db_path='instance/test.db'):
    """Verify test database initialization"""
    try:
        # Check if test database exists
        if not os.path.exists(db_path):
            logging.error(f"Test database not found at {db_path}")
            return False
            
        # Verify schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for required tables
        required_tables = ['stipend', 'tag', 'organization', 'user']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in tables]
        if missing_tables:
            logging.error(f"Missing required tables: {', '.join(missing_tables)}")
            return False
            
        # Verify relationships
        cursor.execute("PRAGMA foreign_key_list('stipend')")
        foreign_keys = cursor.fetchall()
        if not foreign_keys:
            logging.error("No foreign key relationships found")
            return False
            
        logging.info(f"Test database verified successfully at {db_path}")
        return True
        
    except Exception as e:
        logging.error(f"Test database verification failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'instance/test.db'
    verify_test_db(db_path)

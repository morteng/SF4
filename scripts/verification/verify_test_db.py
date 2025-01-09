import os
import sys
import sqlite3
from pathlib import Path
import logging

from app.factory import create_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def verify_test_db(db_path='instance/test.db'):
    """Verify test database initialization with proper app context"""
    try:
        app = create_app('testing')
        with app.app_context():
            # Check if test database exists
            if not os.path.exists(db_path):
                logging.error(f"Test database not found at {db_path}")
                return False
            
            # Verify schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check for required tables
            required_tables = ['stipend', 'tag', 'organization', 'user', 'audit_log']
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
                
            # Verify indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            required_indexes = ['ix_stipend_name', 'ix_tag_name']
            missing_indexes = [idx for idx in required_indexes if idx not in indexes]
            if missing_indexes:
                logging.error(f"Missing required indexes: {', '.join(missing_indexes)}")
                return False
                
            # Verify test data
            cursor.execute("SELECT COUNT(*) FROM stipend")
            stipend_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tag")
            tag_count = cursor.fetchone()[0]
            if stipend_count < 10 or tag_count < 5:
                logging.error(f"Test data insufficient - {stipend_count} stipends and {tag_count} tags found")
                return False
                
            logging.info(f"Test database verified successfully at {db_path}")
            return True
            
    except Exception as e:
        logging.error(f"Test database verification failed: {str(e)}", exc_info=True)
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'instance/test.db'
    verify_test_db(db_path)

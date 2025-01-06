import os
import sys
import sqlite3
from pathlib import Path

def verify_test_db():
    """Verify test database initialization"""
    try:
        # Check if test database exists
        if not os.path.exists('instance/test.db'):
            print("Test database not found")
            return False
            
        # Verify schema
        conn = sqlite3.connect('instance/test.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in test database")
            return False
            
        print("Test database verified successfully")
        return True
        
    except Exception as e:
        print(f"Test database verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    verify_test_db()

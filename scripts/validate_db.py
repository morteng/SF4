import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.version import validate_db_connection

if __name__ == "__main__":
    # Check both production and test databases
    for db_path in ['instance/stipend.db', 'instance/test_stipend.db']:
        print(f"Validating database: {db_path}")
        if validate_db_connection(db_path):
            print("Database connection validation passed")
        else:
            print("Database connection validation failed")
            exit(1)
    exit(0)

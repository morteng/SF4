import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.version import validate_db_connection

if __name__ == "__main__":
    if validate_db_connection('instance/stipend.db'):
        print("Database connection validation passed")
        exit(0)
    else:
        print("Database connection validation failed")
        exit(1)

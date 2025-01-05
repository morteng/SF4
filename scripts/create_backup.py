import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.version import create_db_backup
from datetime import datetime

if __name__ == "__main__":
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backups/stipend_{timestamp}.db'
        os.makedirs('backups', exist_ok=True)
        
        if create_db_backup('instance/stipend.db', backup_file):
            print(f"Created backup: {backup_file}")
            exit(0)
        else:
            print("Backup failed")
            exit(1)
    except Exception as e:
        print(f"Backup failed with error: {str(e)}")
        exit(1)

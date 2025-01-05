import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.version import create_db_backup
from datetime import datetime

if __name__ == "__main__":
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backups/stipend_{timestamp}.db'
    if create_db_backup('instance/stipend.db', backup_file):
        print(f"Created backup: {backup_file}")
        exit(0)
    else:
        print("Backup failed")
        exit(1)

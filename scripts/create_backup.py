from scripts.version import create_db_backup
from datetime import datetime
if __name__ == "__main__":
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backups/stipend_{timestamp}.db'
    create_db_backup('instance/stipend.db', backup_file)
    print(f"Created backup: {backup_file}")
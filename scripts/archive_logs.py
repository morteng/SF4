from scripts.version import archive_logs
from datetime import datetime
if __name__ == "__main__":
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_file = f'logs/archive_{timestamp}.zip'
    archive_logs(archive_file)
    print(f"Created log archive: {archive_file}")
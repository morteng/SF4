import os
import sys
from datetime import datetime
from pathlib import Path
import zipfile

def archive_logs():
    """Archive current logs to a timestamped file"""
    try:
        log_dir = Path('logs')
        if not log_dir.exists():
            print("No logs directory found")
            return False
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_path = log_dir / f'archive_{timestamp}.zip'
        
        with zipfile.ZipFile(archive_path, 'w') as archive:
            for log_file in log_dir.glob('*.log'):
                archive.write(log_file, log_file.name)
                
        print(f"Created log archive: {archive_path}")
        return True
    except Exception as e:
        print(f"Log archiving failed: {str(e)}")
        return False

if __name__ == "__main__":
    archive_logs()

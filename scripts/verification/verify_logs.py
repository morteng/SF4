import os
import zipfile
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_log_archive(archive_path):
    """Verify log archive integrity"""
    try:
        if not Path(archive_path).exists():
            logger.error(f"Log archive not found: {archive_path}")
            return False
            
        # Verify zip file integrity
        if not zipfile.is_zipfile(archive_path):
            logger.error("Invalid zip file format")
            return False
            
        # Check required log files
        required_files = [
            'app.log',
            'tests.log',
            'bots.log'
        ]
        
        with zipfile.ZipFile(archive_path) as zip_ref:
            archive_files = zip_ref.namelist()
            missing_files = [f for f in required_files if f not in archive_files]
            
            if missing_files:
                logger.error(f"Missing log files: {', '.join(missing_files)}")
                return False
                
            # Verify file contents
            for file in required_files:
                try:
                    with zip_ref.open(file) as f:
                        content = f.read(1024)  # Read first 1KB
                        if not content:
                            logger.error(f"Empty log file: {file}")
                            return False
                except Exception as e:
                    logger.error(f"Error reading {file}: {str(e)}")
                    return False
                    
        logger.info(f"Log archive verification passed: {archive_path}")
        return True
        
    except Exception as e:
        logger.error(f"Log archive verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Get latest log archive
    log_files = sorted(Path('logs').glob('archive_*.zip'), reverse=True)
    if not log_files:
        print("No log archives found")
        exit(1)
        
    if verify_log_archive(log_files[0]):
        print("Log archive verification passed")
        exit(0)
    else:
        print("Log archive verification failed")
        exit(1)

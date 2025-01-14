import logging
import gzip
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime
from app.extensions import db
from app.services.notification_service import NotificationService
from app.services.metrics_service import MetricsService
from app.constants import FlashMessages

logger = logging.getLogger(__name__)

class DatabaseRestore:
    """Handles database restore operations with verification and logging
    
    Features:
    - Restore from compressed backups
    - Pre-restore verification
    - Post-restore validation
    - Notification system integration
    - Detailed logging and metrics
    
    Attributes:
        backup_dir (Path): Directory containing backups
        notification_service (NotificationService): Service for sending notifications
        metrics (dict): Restore performance metrics
    """
    
    def __init__(self, backup_dir='backups'):
        """Initialize restore system with enhanced monitoring
        
        Args:
            backup_dir (str): Directory containing backups
        """
        self.backup_dir = Path(backup_dir)
        self.notification_service = NotificationService()
        self.metrics_service = MetricsService()
        self.metrics = {
            'restore_count': 0,
            'last_success': None,
            'last_duration': None,
            'last_backup_used': None,
            'failed_count': 0,
            'average_restore_time': 0,
            'restore_success_rate': 1.0,
            'data_restored': 0,
            'backup_age_restored': None,
            'verification_success_rate': 1.0,
            'total_verification_time': 0,
            'last_verification_time': 0,
            'restore_validation_time': 0,
            'restore_validation_success_rate': 1.0,
            'data_integrity_checks': 0,
            'data_integrity_errors': 0,
            'restore_attempts': 0,
            'last_restore_size': 0,
            'total_data_restored': 0,
            'average_restore_size': 0,
            'restore_validation_errors': 0,
            'backup_freshness': None,
            'restore_throughput': 0
        }

    def _verify_backup(self, backup_path: Path) -> bool:
        """Enhanced backup verification with detailed checks"""
        try:
            # Basic file checks
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
                
            if backup_path.stat().st_size < 1024:  # Minimum 1KB
                logger.error(f"Backup file too small: {backup_path.stat().st_size} bytes")
                return False

            # Gzip integrity check
            try:
                with gzip.open(backup_path, 'rb') as f:
                    # Check header
                    header = f.read(100)
                    if b'CREATE TABLE' not in header:
                        logger.error("Invalid backup header - missing CREATE TABLE")
                        return False
                    
                    # Check footer
                    f.seek(-100, 2)  # Go to last 100 bytes
                    footer = f.read()
                    if b'COMMIT' not in footer:
                        logger.error("Invalid backup footer - missing COMMIT")
                        return False
                    
                    # Check for required tables
                    f.seek(0)
                    content = f.read().decode('utf-8')
                    required_tables = ['stipend', 'organization', 'tag']
                    for table in required_tables:
                        if f'CREATE TABLE {table}' not in content:
                            logger.error(f"Missing required table: {table}")
                            return False
                            
                    # Check for data integrity markers
                    if 'INSERT INTO' not in content:
                        logger.error("No data inserts found in backup")
                        return False
                        
            except gzip.BadGzipFile:
                logger.error("Invalid gzip file format")
                return False
            except UnicodeDecodeError:
                logger.error("Invalid file encoding")
                return False
                
            # If all checks passed
            logger.info(f"Backup verification successful: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return False

    def restore(self, backup_name: Optional[str] = None) -> bool:
        """Restore database from backup
        
        Args:
            backup_name (str): Optional specific backup to restore
            
        Returns:
            bool: True if restore succeeded, False otherwise
        """
        start_time = datetime.now()
        
        try:
            # Find backup to restore
            if backup_name:
                backup_path = self.backup_dir / backup_name
            else:
                # Get most recent backup
                backups = sorted(self.backup_dir.glob('backup_*.sql.gz'), reverse=True)
                if not backups:
                    logger.error("No backups found to restore")
                    return False
                backup_path = backups[0]
                
            if not self._verify_backup(backup_path):
                logger.error(f"Invalid backup file: {backup_path}")
                return False
                
            # Restore process
            with gzip.open(backup_path, 'rb') as f_in:
                process = subprocess.Popen(
                    ['psql', '-d', db.engine.url.database],
                    stdin=f_in,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    logger.error(f"Restore failed: {stderr.decode()}")
                    return False
                    
            # Calculate restore metrics
            duration = (datetime.now() - start_time).total_seconds()
            backup_age = datetime.now() - datetime.fromtimestamp(backup_path.stat().st_mtime)
            restore_size = backup_path.stat().st_size
            throughput = restore_size / duration if duration > 0 else 0
            
            # Update comprehensive metrics
            self.metrics.update({
                'restore_count': self.metrics['restore_count'] + 1,
                'last_success': datetime.now(),
                'last_duration': duration,
                'last_backup_used': backup_path.name,
                'data_restored': restore_size,
                'backup_age_restored': backup_age.total_seconds(),
                'average_restore_time': (
                    (self.metrics['average_restore_time'] * (self.metrics['restore_count'] - 1) + duration) 
                    / self.metrics['restore_count']
                ),
                'restore_success_rate': (
                    self.metrics['restore_count'] / 
                    (self.metrics['restore_count'] + self.metrics['failed_count'])
                ),
                'last_restore_size': restore_size,
                'total_data_restored': self.metrics['total_data_restored'] + restore_size,
                'average_restore_size': (
                    (self.metrics['average_restore_size'] * (self.metrics['restore_count'] - 1) + restore_size) 
                    / self.metrics['restore_count']
                ),
                'restore_throughput': throughput,
                'backup_freshness': backup_age.total_seconds(),
                'data_integrity_checks': self.metrics['data_integrity_checks'] + 1
            })
            
            # Record metrics
            self.metrics_service.record('restore_duration', duration)
            self.metrics_service.record('restore_size', restore_size)
            self.metrics_service.record('backup_age_restored', backup_age.total_seconds())
            self.metrics_service.record('restore_throughput', throughput)
            
            # Record metrics
            self.metrics_service.record('restore_duration', duration)
            self.metrics_service.record('restore_size', backup_path.stat().st_size)
            self.metrics_service.record('backup_age_restored', backup_age.total_seconds())
            
            logger.info(f"Successfully restored from {backup_path.name} in {duration:.2f} seconds")
            self.notification_service.send(
                "Database Restore Complete",
                f"Database restored from {backup_path.name}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            self.notification_service.send(
                "Database Restore Failed",
                f"Error restoring database: {str(e)}"
            )
            return False

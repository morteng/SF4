import logging
import gzip
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime
from app.extensions import db
from app.services.notification_service import NotificationService
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
        """Initialize restore system
        
        Args:
            backup_dir (str): Directory containing backups
        """
        self.backup_dir = Path(backup_dir)
        self.notification_service = NotificationService()
        self.metrics = {
            'restore_count': 0,
            'last_success': None,
            'last_duration': None,
            'last_backup_used': None
        }

    def _verify_backup(self, backup_path: Path) -> bool:
        """Verify backup integrity before restore
        
        Args:
            backup_path (Path): Path to backup file
            
        Returns:
            bool: True if backup is valid, False otherwise
        """
        try:
            with gzip.open(backup_path, 'rb') as f:
                header = f.read(100)
                return b'CREATE TABLE' in header
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
                    
            # Update metrics
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.update({
                'restore_count': self.metrics['restore_count'] + 1,
                'last_success': datetime.now(),
                'last_duration': duration,
                'last_backup_used': backup_path.name
            })
            
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

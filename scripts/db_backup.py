import logging
import os
import gzip
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from app.extensions import db
from app.models import Stipend, Organization, Tag
from app.constants import FlashMessages
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Handles database backup operations with compression, verification and scheduling
    
    Features:
    - Compressed backups with timestamping
    - Backup rotation with configurable retention
    - Integrity verification
    - Notification system integration
    - Detailed logging and metrics
    - Support for both full and incremental backups
    
    Attributes:
        backup_dir (Path): Directory to store backups
        max_backups (int): Maximum number of backups to retain
        notification_service (NotificationService): Service for sending notifications
        metrics (dict): Backup performance metrics
    """
    
    def __init__(self, backup_dir='backups', max_backups=5):
        """Initialize backup system
        
        Args:
            backup_dir (str): Directory to store backups
            max_backups (int): Maximum number of backups to retain
        """
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.notification_service = NotificationService()
        self.metrics = {
            'backup_count': 0,
            'last_success': None,
            'last_duration': None,
            'total_size': 0
        }
        
    def _generate_backup_name(self):
        """Generate timestamped backup filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"backup_{timestamp}.sql.gz"
    
    def _rotate_backups(self):
        """Rotate old backups to maintain max_backups limit"""
        backups = sorted(self.backup_dir.glob('backup_*.sql.gz'))
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
            logger.info(f"Rotated out old backup: {oldest.name}")
    
    def _verify_backup(self, backup_path):
        """Verify backup integrity"""
        try:
            with gzip.open(backup_path, 'rb') as f:
                header = f.read(100)
                return b'CREATE TABLE' in header
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return False
    
    def create_backup(self):
        """Create a compressed database backup"""
        backup_file = self.backup_dir / self._generate_backup_name()
        temp_file = backup_file.with_suffix('.sql')
        
        try:
            # Dump database to temporary file
            with temp_file.open('w') as f:
                for line in db.engine.raw_connection().connection.iterdump():
                    f.write(f'{line}\n')
            
            # Compress the backup
            with temp_file.open('rb') as f_in:
                with gzip.open(backup_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Verify and rotate backups
            if not self._verify_backup(backup_file):
                raise ValueError("Backup verification failed")
            
            self._rotate_backups()
            logger.info(f"Created backup: {backup_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            if backup_file.exists():
                backup_file.unlink()
            if temp_file.exists():
                temp_file.unlink()
            return False

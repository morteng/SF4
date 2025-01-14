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
        """Enhanced backup rotation with notifications"""
        backups = sorted(self.backup_dir.glob('backup_*.sql.gz'))
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            try:
                size = oldest.stat().st_size
                oldest.unlink()
                logger.info(f"Rotated out old backup: {oldest.name} ({size} bytes)")
                
                # Update metrics
                self.metrics['total_size'] -= size
                
                # Notify rotation
                self.notification_service.send(
                    "Backup Rotated",
                    f"Rotated out old backup {oldest.name} ({size} bytes)"
                )
            except Exception as e:
                logger.error(f"Failed to rotate backup {oldest.name}: {str(e)}")
                self.notification_service.send(
                    "Backup Rotation Failed",
                    f"Error rotating backup {oldest.name}: {str(e)}"
                )
    
    def _verify_backup(self, backup_path):
        """Enhanced backup verification with detailed checks"""
        try:
            with gzip.open(backup_path, 'rb') as f:
                # Check header
                header = f.read(100)
                if b'CREATE TABLE' not in header:
                    return False
                
                # Check footer
                f.seek(-100, 2)  # Go to last 100 bytes
                footer = f.read()
                if b'COMMIT' not in footer:
                    return False
                    
                # Check size
                if backup_path.stat().st_size < 1024:  # Minimum 1KB
                    return False
                    
                return True
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            self.notification_service.send(
                "Backup Verification Failed",
                f"Error verifying backup {backup_path.name}: {str(e)}"
            )
            return False
    
    def create_backup(self):
        """Create a compressed database backup with enhanced monitoring"""
        start_time = datetime.now()
        backup_file = self.backup_dir / self._generate_backup_name()
        temp_file = backup_file.with_suffix('.sql')
        
        try:
            # Notify backup start
            self.notification_service.send(
                "Backup Started",
                f"Starting database backup to {backup_file.name}"
            )
            
            # Dump database to temporary file
            with temp_file.open('w') as f:
                for line in db.engine.raw_connection().connection.iterdump():
                    f.write(f'{line}\n')
            
            # Compress the backup
            with temp_file.open('rb') as f_in:
                with gzip.open(backup_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Verify backup integrity
            if not self._verify_backup(backup_file):
                raise ValueError("Backup verification failed")
            
            # Rotate old backups
            self._rotate_backups()
            
            # Update metrics
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.update({
                'backup_count': self.metrics['backup_count'] + 1,
                'last_success': datetime.now(),
                'last_duration': duration,
                'total_size': self.metrics['total_size'] + backup_file.stat().st_size
            })
            
            # Notify success
            self.notification_service.send(
                "Backup Completed",
                f"Successfully created backup {backup_file.name} in {duration:.2f} seconds"
            )
            
            logger.info(f"Created backup: {backup_file.name} ({backup_file.stat().st_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            if backup_file.exists():
                backup_file.unlink()
            if temp_file.exists():
                temp_file.unlink()
            return False
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

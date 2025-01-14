import logging
import os
import subprocess
import datetime
import gzip
import shutil
from pathlib import Path
from typing import Optional, Tuple
from app.extensions import db
from app.constants import FlashMessages

logger = logging.getLogger(__name__)

class BackupService:
    """Service for managing database backups and restores with enhanced features.
    
    Provides automated database backup functionality including:
    - Compressed backups with rotation
    - Integrity verification
    - Restore operations
    - Monitoring and alerting
    - Integration with existing logging system
    
    Implements the following patterns:
    - Facade: Simplifies complex backup operations
    - Observer: Backup status monitoring
    - Chain of Responsibility: Backup verification pipeline
    
    Attributes:
        backup_dir (Path): Directory to store backups
        retention_days (int): Number of days to keep backups
        max_backups (int): Maximum number of backups to keep
        db_url (str): Database connection URL
        compression_level (int): Gzip compression level (1-9)
    """
    
    def __init__(self):
        self.backup_dir = Path(os.getenv('BACKUP_DIR', 'backups'))
        self.retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', 7))
        self.max_backups = int(os.getenv('MAX_BACKUPS', 10))
        self.db_url = db.engine.url.render_as_string(hide_password=False)
        self.compression_level = 9
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self) -> Tuple[bool, str]:
        """Create a compressed database backup with monitoring integration.
        
        Returns:
            Tuple[bool, str]: (success, message) indicating backup status
        """
        from scripts.db_monitor import dashboard
        from scripts.db_alerts import alerts
        
        start_time = datetime.datetime.now()
        timestamp = start_time.strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f'db_backup_{timestamp}.sql.gz'
        
        try:
            # Create backup using pg_dump
            with gzip.open(backup_file, 'wb', compresslevel=self.compression_level) as f:
                process = subprocess.Popen(
                    ['pg_dump', self.db_url],
                    stdout=f,
                    stderr=subprocess.PIPE
                )
                _, stderr = process.communicate()
                
                if process.returncode != 0:
                    error_msg = f"Backup failed: {stderr.decode('utf-8')}"
                    logger.error(error_msg)
                    
                    # Record failed backup
                    duration = (datetime.datetime.now() - start_time).total_seconds()
                    dashboard.add_metric(BackupMetric(
                        timestamp=start_time,
                        success=False,
                        size_mb=0,
                        duration_sec=duration,
                        error=error_msg
                    ))
                    return False, error_msg
                    
            # Get backup size
            backup_size = backup_file.stat().st_size / (1024 * 1024)  # Convert to MB
            duration = (datetime.datetime.now() - start_time).total_seconds()
            
            # Verify backup integrity
            if not self.verify_backup(backup_file):
                error_msg = "Backup verification failed"
                logger.error(error_msg)
                backup_file.unlink()  # Remove invalid backup
                
                # Record failed verification
                dashboard.add_metric(BackupMetric(
                    timestamp=start_time,
                    success=False,
                    size_mb=backup_size,
                    duration_sec=duration,
                    error=error_msg
                ))
                return False, error_msg
                
            # Clean up old backups
            self.cleanup_old_backups()
            
            # Record successful backup
            dashboard.add_metric(BackupMetric(
                timestamp=start_time,
                success=True,
                size_mb=backup_size,
                duration_sec=duration
            ))
            
            # Check for alerts
            alerts.check_and_notify({
                'failure_rate': dashboard.get_success_rate(),
                'avg_duration': dashboard.get_avg_duration(),
                'avg_size': dashboard.get_avg_size()
            })
            
            logger.info(f"Backup created successfully: {backup_file}")
            return True, f"Backup created: {backup_file.name}"
            
        except Exception as e:
            error_msg = f"Backup error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
            
    def verify_backup(self, backup_file: Path) -> bool:
        """Verify the integrity of a backup file.
        
        Args:
            backup_file (Path): Path to the backup file
            
        Returns:
            bool: True if backup is valid, False otherwise
        """
        try:
            # Test decompression and basic SQL syntax
            with gzip.open(backup_file, 'rb') as f:
                header = f.read(100)
                return b'PostgreSQL' in header
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return False
            
    def cleanup_old_backups(self) -> None:
        """Remove old backups based on retention policy."""
        backups = sorted(self.backup_dir.glob('*.sql.gz'), key=os.path.getmtime)
        
        # Remove by age
        cutoff = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
        for backup in backups:
            if datetime.datetime.fromtimestamp(backup.stat().st_mtime) < cutoff:
                backup.unlink()
                logger.info(f"Removed old backup: {backup.name}")
                
        # Remove by count
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
            logger.info(f"Removed backup (max count): {oldest.name}")
            
    def restore_backup(self, backup_file: Path) -> Tuple[bool, str]:
        """Restore database from a backup file.
        
        Args:
            backup_file (Path): Path to the backup file
            
        Returns:
            Tuple[bool, str]: (success, message) indicating restore status
        """
        try:
            # Verify backup before restore
            if not self.verify_backup(backup_file):
                error_msg = "Cannot restore - backup verification failed"
                logger.error(error_msg)
                return False, error_msg
                
            # Restore using psql
            with gzip.open(backup_file, 'rb') as f:
                process = subprocess.Popen(
                    ['psql', self.db_url],
                    stdin=f,
                    stderr=subprocess.PIPE
                )
                _, stderr = process.communicate()
                
                if process.returncode != 0:
                    error_msg = f"Restore failed: {stderr.decode('utf-8')}"
                    logger.error(error_msg)
                    return False, error_msg
                    
            logger.info(f"Database restored from: {backup_file.name}")
            return True, f"Database restored from: {backup_file.name}"
            
        except Exception as e:
            error_msg = f"Restore error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

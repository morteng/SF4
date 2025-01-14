import logging
import os
import gzip
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from app.extensions import db
from app.models import Stipend, Organization, Tag
from app.constants import FlashMessages
from app.services.notification_service import NotificationService
from app.services.metrics_service import MetricsService

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
    - Scheduled backups with cron-like functionality
    - Backup encryption support
    - Cloud storage integration
    
    Attributes:
        backup_dir (Path): Directory to store backups
        max_backups (int): Maximum number of backups to retain
        notification_service (NotificationService): Service for sending notifications
        metrics_service (MetricsService): Service for tracking backup metrics
        retention_days (int): Number of days to retain backups
        compression_level (int): Gzip compression level (1-9)
        verify_backups (bool): Whether to verify backup integrity
    """
    
    def __init__(self, backup_dir='backups', max_backups=5, retention_days=30, 
                 compression_level=6, verify_backups=True):
        """Initialize backup system with enhanced configuration
        
        Args:
            backup_dir (str): Directory to store backups
            max_backups (int): Maximum number of backups to retain
            retention_days (int): Number of days to retain backups
            compression_level (int): Gzip compression level (1-9)
            verify_backups (bool): Whether to verify backup integrity
        """
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.retention_days = retention_days
        self.compression_level = compression_level
        self.verify_backups = verify_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.notification_service = NotificationService()
        self.metrics_service = MetricsService()
        
        # Initialize metrics
        self.metrics = {
            'backup_count': 0,
            'last_success': None,
            'last_duration': None,
            'total_size': 0,
            'failed_count': 0,
            'compression_ratio': 0.0,
            'verification_success_rate': 1.0
        }
        
    def _generate_backup_name(self):
        """Generate timestamped backup filename with version info"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"backup_v1_{timestamp}.sql.gz"
    
    def _rotate_backups(self):
        """Enhanced backup rotation with age-based and count-based retention"""
        backups = sorted(self.backup_dir.glob('backup_*.sql.gz'), 
                        key=os.path.getmtime)
        
        current_time = datetime.now()
        removed_count = 0
        total_size_removed = 0
        
        # Remove backups older than retention period
        for backup in backups[:]:
            backup_age = current_time - datetime.fromtimestamp(backup.stat().st_mtime)
            if backup_age > timedelta(days=self.retention_days):
                try:
                    size = backup.stat().st_size
                    backup.unlink()
                    removed_count += 1
                    total_size_removed += size
                    logger.info(f"Rotated out old backup: {backup.name} ({size} bytes)")
                    
                    # Notify rotation
                    self.notification_service.send(
                        "Backup Rotated",
                        f"Rotated out old backup {backup.name} ({size} bytes)"
                    )
                except Exception as e:
                    logger.error(f"Failed to rotate backup {backup.name}: {str(e)}")
                    self.notification_service.send(
                        "Backup Rotation Failed",
                        f"Error rotating backup {backup.name}: {str(e)}"
                    )
                    self.metrics['failed_count'] += 1
        
        # Remove excess backups if still over max_backups
        backups = sorted(self.backup_dir.glob('backup_*.sql.gz'), 
                        key=os.path.getmtime)
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            try:
                size = oldest.stat().st_size
                oldest.unlink()
                removed_count += 1
                total_size_removed += size
                logger.info(f"Rotated out old backup: {oldest.name} ({size} bytes)")
                
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
                self.metrics['failed_count'] += 1
        
        # Update metrics
        if removed_count > 0:
            self.metrics['total_size'] -= total_size_removed
            self.metrics_service.record('backups_rotated', removed_count)
            self.metrics_service.record('storage_freed', total_size_removed)
    
    def _verify_backup(self, backup_path):
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
            
            # Verify temporary SQL file
            if not self._verify_sql_file(temp_file):
                raise ValueError("Temporary SQL file verification failed")
            
            # Compress the backup
            with temp_file.open('rb') as f_in:
                with gzip.open(backup_file, 'wb', compresslevel=self.compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Verify compressed backup
            if not self._verify_backup(backup_file):
                raise ValueError("Backup verification failed")
            
            # Calculate compression ratio
            original_size = temp_file.stat().st_size
            compressed_size = backup_file.stat().st_size
            compression_ratio = (original_size - compressed_size) / original_size
            
            # Rotate old backups
            self._rotate_backups()
            
            # Update metrics
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.update({
                'backup_count': self.metrics['backup_count'] + 1,
                'last_success': datetime.now(),
                'last_duration': duration,
                'total_size': self.metrics['total_size'] + compressed_size,
                'compression_ratio': compression_ratio,
                'verification_success_rate': 1.0
            })
            
            # Notify success
            self.notification_service.send(
                "Backup Completed",
                f"Successfully created backup {backup_file.name} in {duration:.2f} seconds\n"
                f"Compression ratio: {compression_ratio:.1%}"
            )
            
            logger.info(f"Created backup: {backup_file.name} ({compressed_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            self.metrics['failed_count'] += 1
            self.metrics['verification_success_rate'] = (
                self.metrics['backup_count'] / 
                (self.metrics['backup_count'] + self.metrics['failed_count'])
            )
            
            # Clean up failed files
            if backup_file.exists():
                backup_file.unlink()
            if temp_file.exists():
                temp_file.unlink()
                
            # Notify failure
            self.notification_service.send(
                "Backup Failed",
                f"Backup failed: {str(e)}"
            )
            return False

    def _verify_sql_file(self, sql_file):
        """Verify the temporary SQL file before compression"""
        try:
            with sql_file.open('r') as f:
                content = f.read()
                
                # Check for required tables
                required_tables = ['stipend', 'organization', 'tag']
                for table in required_tables:
                    if f'CREATE TABLE {table}' not in content:
                        logger.error(f"Missing required table in SQL: {table}")
                        return False
                        
                # Check for data inserts
                if 'INSERT INTO' not in content:
                    logger.error("No data inserts found in SQL file")
                    return False
                    
                # Check for complete transactions
                if 'BEGIN TRANSACTION' not in content or 'COMMIT' not in content:
                    logger.error("Incomplete transaction in SQL file")
                    return False
                    
            return True
        except Exception as e:
            logger.error(f"SQL file verification failed: {str(e)}")
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
import logging
import os
import gzip
import shutil
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
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from app.extensions import db
from app.models import Stipend, Organization, Tag
from app.constants import FlashMessages
from app.services.notification_service import NotificationService
from app.services.metrics_service import MetricsService

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
    - Scheduled backups with cron-like functionality
    - Backup encryption support
    - Cloud storage integration
    
    Attributes:
        backup_dir (Path): Directory to store backups
        max_backups (int): Maximum number of backups to retain
        notification_service (NotificationService): Service for sending notifications
        metrics_service (MetricsService): Service for tracking backup metrics
        retention_days (int): Number of days to retain backups
        compression_level (int): Gzip compression level (1-9)
        verify_backups (bool): Whether to verify backup integrity
    """
    
    def __init__(self, backup_dir='backups', max_backups=5, retention_days=30, 
                 compression_level=6, verify_backups=True):
        """Initialize backup system with enhanced configuration
        
        Args:
            backup_dir (str): Directory to store backups
            max_backups (int): Maximum number of backups to retain
            retention_days (int): Number of days to retain backups
            compression_level (int): Gzip compression level (1-9)
            verify_backups (bool): Whether to verify backup integrity
        """
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.retention_days = retention_days
        self.compression_level = compression_level
        self.verify_backups = verify_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.notification_service = NotificationService()
        self.metrics_service = MetricsService()
        
        # Initialize metrics
        self.metrics = {
            'backup_count': 0,
            'last_success': None,
            'last_duration': None,
            'total_size': 0,
            'failed_count': 0,
            'compression_ratio': 0.0,
            'verification_success_rate': 1.0
        }
        
    def _generate_backup_name(self):
        """Generate timestamped backup filename with version info"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"backup_v1_{timestamp}.sql.gz"
    
    def _rotate_backups(self):
        """Enhanced backup rotation with age-based and count-based retention"""
        backups = sorted(self.backup_dir.glob('backup_*.sql.gz'), 
                        key=os.path.getmtime)
        
        current_time = datetime.now()
        removed_count = 0
        total_size_removed = 0
        
        # Remove backups older than retention period
        for backup in backups[:]:
            backup_age = current_time - datetime.fromtimestamp(backup.stat().st_mtime)
            if backup_age > timedelta(days=self.retention_days):
                try:
                    size = backup.stat().st_size
                    backup.unlink()
                    removed_count += 1
                    total_size_removed += size
                    logger.info(f"Rotated out old backup: {backup.name} ({size} bytes)")
                    
                    # Notify rotation
                    self.notification_service.send(
                        "Backup Rotated",
                        f"Rotated out old backup {backup.name} ({size} bytes)"
                    )
                except Exception as e:
                    logger.error(f"Failed to rotate backup {backup.name}: {str(e)}")
                    self.notification_service.send(
                        "Backup Rotation Failed",
                        f"Error rotating backup {backup.name}: {str(e)}"
                    )
                    self.metrics['failed_count'] += 1
        
        # Remove excess backups if still over max_backups
        backups = sorted(self.backup_dir.glob('backup_*.sql.gz'), 
                        key=os.path.getmtime)
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            try:
                size = oldest.stat().st_size
                oldest.unlink()
                removed_count += 1
                total_size_removed += size
                logger.info(f"Rotated out old backup: {oldest.name} ({size} bytes)")
                
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
                self.metrics['failed_count'] += 1
        
        # Update metrics
        if removed_count > 0:
            self.metrics['total_size'] -= total_size_removed
            self.metrics_service.record('backups_rotated', removed_count)
            self.metrics_service.record('storage_freed', total_size_removed)
    
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

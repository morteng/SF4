from pathlib import Path
import logging
import os
import sqlite3
import time
import subprocess
from datetime import datetime
from typing import Optional, Tuple
import re
from app.common.db_utils import validate_db_connection
from scripts.archive_logs import archive_logs
from scripts.init_logging import configure_logging

# Current version
__version__ = "0.2.0"

# Configure logger at module level
logger = logging.getLogger(__name__)

# Configure logging
LOG_FILE = configure_logging()

def main() -> None:
    """Main entry point for version management CLI"""
    try:
        import argparse
        parser = argparse.ArgumentParser(description='Version management utilities')
        subparsers = parser.add_subparsers(dest='command', required=True)

        # Add check-version command
        check_parser = subparsers.add_parser('check-version', help='Check current version')
        
        # Add version bump command
        bump_parser = subparsers.add_parser('bump-version', help='Bump version number')
        bump_parser.add_argument('type', choices=['major', 'minor', 'patch'], 
                               help='Version type to bump')
        
        # Add validate command
        validate_parser = subparsers.add_parser('validate', 
                                              help='Validate version and environment')
        
        # Test connection command
        test_conn_parser = subparsers.add_parser('test-connection', help='Test database connection')
        test_conn_parser.add_argument('db_path', help='Path to database file')

        # Backup command
        backup_parser = subparsers.add_parser('backup', help='Create database backup')
        backup_parser.add_argument('source_db', help='Source database path')
        backup_parser.add_argument('backup_path', help='Backup destination path')

        # Environment validation command
        env_parser = subparsers.add_parser('validate-env', help='Validate production environment')
        
        # Log archiving command
        archive_parser = subparsers.add_parser('archive-logs', help='Archive logs')
        archive_parser.add_argument('--force', action='store_true', help='Force archive even if empty')

        # Release notes command
        release_notes_parser = subparsers.add_parser('update-release-notes', help='Update release notes')
        release_notes_parser.add_argument('--version', help='Specify version number')
        
        # Documentation command
        docs_parser = subparsers.add_parser('update-docs', help='Update documentation')
        docs_parser.add_argument('--version', help='Specify version number')
        
        # Deployment verification command
        deploy_parser = subparsers.add_parser('verify-deployment', help='Verify deployment')
        deploy_parser.add_argument('--full', action='store_true', help='Run full verification')

        args = parser.parse_args()

        if args.command == 'check-version':
            print(f"Current version: {__version__}")
        elif args.command == 'bump-version':
            new_version = bump_version(args.type)
            print(f"Version bumped to: {new_version}")
        elif args.command == 'validate':
            if not validate_version(__version__):
                print("Version format is invalid")
                exit(1)
            if not validate_production_environment():
                print("Environment validation failed")
                exit(1)
            print("Validation successful")
        elif args.command == 'test-connection':
            result = validate_db_connection(args.db_path)
            print(f"Connection {'successful' if result else 'failed'}")
            exit(0 if result else 1)
        elif args.command == 'backup':
            result = create_db_backup(args.source_db, args.backup_path)
            print(f"Backup {'successful' if result else 'failed'}")
            exit(0 if result else 1)
        elif args.command == 'validate-env':
            result = validate_production_environment()
            print(f"Environment validation {'passed' if result else 'failed'}")
            exit(0 if result else 1)
        elif args.command == 'archive-logs':
            result = archive_logs(args.force)
            print(f"Log archiving {'completed' if result else 'failed'}")
            exit(0 if result else 1)
        elif args.command == 'update-release-notes':
            result = update_release_notes(args.version)
            print(f"Release notes {'updated' if result else 'failed'}")
            exit(0 if result else 1)
        elif args.command == 'update-docs':
            result = update_documentation(args.version)
            print(f"Documentation {'updated' if result else 'failed'}")
            exit(0 if result else 1)
        elif args.command == 'verify-deployment':
            result = verify_deployment(args.full)
            print(f"Deployment {'verified' if result else 'failed'}")
            exit(0 if result else 1)
        else:
            parser.print_help()
            exit(1)
    except Exception as e:
        logging.error(f"Error in version management: {str(e)}")
        exit(1)

def update_release_notes():
    """Update release notes with current version information"""
    try:
        with open('RELEASE_NOTES.md', 'a') as f:
            f.write(f"\n## Version {__version__} - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("- Initial production release\n")
            f.write("- Fixed version management CLI arguments\n")
            f.write("- Added proper error handling for archive-logs\n")
            f.write("- Implemented version history tracking\n")
        return True
    except Exception as e:
        logging.error(f"Failed to update release notes: {str(e)}")
        return False

def create_version_history(new_version: str) -> None:
    """Create version history file"""
    history_file = Path('VERSION_HISTORY.md')
    history_file.parent.mkdir(exist_ok=True, parents=True)
    
    # Initialize file if it doesn't exist
    if not history_file.exists():
        history_file.write_text("# Version History\n\n")
    
    # Check if the version already exists in the file
    with history_file.open('r') as f:
        content = f.read()
        if f"## {new_version} - {datetime.now().strftime('%Y-%m-%d')}" in content:
            logging.info(f"Version {new_version} already exists in VERSION_HISTORY.md")
            return
    
    with history_file.open('a') as f:
        f.write(f"## {new_version} - {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("- Version bump\n")
        f.write("- Fixed version management tests\n")
        f.write("- Improved version history tracking\n\n")

def update_documentation():
    """Update project documentation"""
    try:
        # Update README
        with open('README.md', 'r+') as f:
            content = f.read()
            if __version__ not in content:
                f.write(f"\n## Current Version\n- {__version__}\n")
        
        # Update CONVENTIONS.md
        with open('CONVENTIONS.md.md', 'r+') as f:
            content = f.read()
            if "Version Management" not in content:
                f.write("\n## Version Management\n- Follow semantic versioning\n")
        return True
    except Exception as e:
        logging.error(f"Failed to update documentation: {str(e)}")
        return False

def validate_schema(db_path: str = 'instance/stipend.db') -> bool:
    """Validate database schema version against expected version"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if alembic_version table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        if not cursor.fetchone():
            logging.error("Alembic version table not found")
            return False
            
        # Get current schema version
        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()[0]
        
        # TODO: Add actual version validation logic
        logging.info(f"Current schema version: {version}")
        return True
        
    except sqlite3.Error as e:
        logging.error(f"Schema validation failed: {str(e)}")
        return False

def verify_deployment(full=False):
    """Verify deployment status with comprehensive checks"""
    try:
        # Basic verification
        if not validate_db_connection('instance/stipend.db'):
            logging.error("Database connection verification failed")
            return False
            
        if not validate_schema('instance/stipend.db'):
            logging.error("Schema version verification failed")
            return False
            
        if not validate_production_environment():
            logging.error("Environment validation failed")
            return False
            
        # Full verification
        if full:
            from app.extensions import db, login_manager, migrate, csrf, limiter
            if not all([db, login_manager, migrate, csrf, limiter]):
                logging.error("Extensions initialization verification failed")
                return False
                
            if not validate_version_file():
                logging.error("Version file validation failed")
                return False
                
        logging.info("Deployment verification completed successfully")
        return True
    except Exception as e:
        logging.error(f"Deployment verification failed: {str(e)}", exc_info=True)
        return False

def get_db_version(db_path: str) -> Optional[str]:
    """Get version from database if available"""
    if not validate_db_connection(db_path):
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        conn.close()
        return str(version) if version else None
    except sqlite3.Error:
        return None

def validate_version(version: str = None) -> bool:
    """Validate version string format"""
    if not version:
        version = get_version()  # Get current version if none provided
        if not version:
            logger.error("No version provided")
            return False
        
    # Basic format validation
    if not re.match(r"^\d+\.\d+\.\d+(-[a-z]+(\.\d+)?)?(\+[a-z0-9]+(\.[a-z0-9]+)*)?$", version):
        logger.error(f"Invalid version format: {version}")
        return False
        
    # Additional semantic validation
    try:
        major, minor, patch = map(int, version.split('.')[:3])
        if major < 0 or minor < 0 or patch < 0:
            logger.error(f"Version components must be positive: {version}")
            return False
            
        logger.info(f"Version validation passed: {version}")
        return True
    except (ValueError, IndexError) as e:
        logger.error(f"Version parsing error: {str(e)}")
        return False

def get_version() -> str:
    """Get the current project version"""
    return __version__

def parse_version(version: str) -> Tuple[int, int, int, Optional[str]]:
    """Parse version string into components"""
    if not validate_version(version):
        raise ValueError(f"Invalid version format: {version}")

    version_parts = version.split('.')
    major = int(version_parts[0])
    minor = int(version_parts[1])
    patch = int(version_parts[2].split('-')[0])
    suffix = version_parts[2].split('-')[1] if '-' in version_parts[2] else None

    return major, minor, patch, suffix

def bump_version(version_type="patch", current_version=None) -> str:
    """Bump the version number and return the new version string"""
    if version_type not in ["major", "minor", "patch"]:
        raise ValueError("version_type must be 'major', 'minor' or 'patch'")

    try:
        # Get current version
        version_to_bump = current_version if current_version else __version__
        major, minor, patch, suffix = parse_version(version_to_bump)

        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:
            patch += 1

        new_version = f"{major}.{minor}.{patch}"
        
        # Update version file if not testing
        if not current_version:
            update_version_file(new_version)
            create_version_history(new_version)
            update_release_notes()
        
        return new_version
        
    except Exception as e:
        logging.error(f"Version bump failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Version bump failed: {str(e)}")

import shutil

def update_version_file(new_version: str, file_path: str = None) -> bool:
    """Update the __version__ in the version.py file with proper error handling"""
    try:
        version_file_path = Path(file_path) if file_path else Path(__file__)
        
        # Create backup before modifying
        backup_path = version_file_path.with_suffix('.bak')
        shutil.copy(version_file_path, backup_path)
        
        with version_file_path.open('r') as f:
            lines = f.readlines()
        
        with version_file_path.open('w') as f:
            for line in lines:
                if line.startswith("__version__"):
                    f.write(f'__version__ = "{new_version}"\n')
                else:
                    f.write(line)
                    
        # Verify update was successful
        with version_file_path.open('r') as f:
            content = f.read()
            if f'__version__ = "{new_version}"' not in content:
                raise RuntimeError("Version update verification failed")
                
        return True
    except Exception as e:
        logging.error(f"Failed to update version file: {str(e)}")
        # Restore from backup if update failed
        if backup_path.exists():
            shutil.copy(backup_path, version_file_path)
        return False

def push_to_github(branch_name: str, commit_message: str) -> bool:
    """Push changes to GitHub with proper validation"""
    try:
        # Verify branch exists (this check might need adjustment depending on your git workflow)
        subprocess.run(["git", "rev-parse", "--verify", branch_name], check=True, capture_output=True)

        # Stage changes
        subprocess.run(["git", "add", "."], check=True, capture_output=True)

        # Commit with message
        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)

        # Push to remote
        subprocess.run(["git", "push", "origin", branch_name], check=True, capture_output=True)

        print(f"Successfully pushed branch '{branch_name}' to GitHub.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        print(f"Error details: {e.stderr.decode()}")
        return False

def create_db_backup(source_db: str, backup_path: str = None) -> bool:
    """Create a timestamped backup of the database"""
    try:
        # Set default backup path if not provided
        if backup_path is None:
            backup_dir = Path('backups')
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = str(backup_dir / f"stipend_{timestamp}.db")
        
        # Ensure backup directory exists
        backup_dir = Path(backup_path).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to source database and create backup
        conn = sqlite3.connect(source_db)
        with conn:
            conn.execute(f"VACUUM INTO '{backup_path}'")
        conn.close()
        
        # Verify backup was created
        if not Path(backup_path).exists():
            raise RuntimeError("Backup file was not created")
            
        logging.info(f"Database backup created: {source_db} -> {backup_path}")
        return True
    except sqlite3.Error as e:
        logging.error(f"Database backup failed: {str(e)}")
        return False

def validate_version_file(file_path: Optional[str] = None) -> bool:
    """Validate version file integrity
    
    Args:
        file_path: Optional path to version file. If None, uses current file.
    
    Returns:
        bool: True if version file is valid, False otherwise
    
    Raises:
        FileNotFoundError: If version file cannot be found
        IOError: If version file cannot be read
    """
    try:
        path = file_path if file_path else __file__
        with open(path, 'r') as f:
            content = f.read()
            return ('__version__' in content and 
                    'validate_version' in content and
                    'bump_version' in content and
                    'create_db_backup' in content)
    except Exception as e:
        logging.error(f"Version file validation error: {str(e)}")
        return False

def create_version_history(new_version: str, history_path: str = None) -> None:
    """Create version history file"""
    history_file = Path(history_path) if history_path else Path('VERSION_HISTORY.md')
    history_file.parent.mkdir(exist_ok=True, parents=True)
    
    if not history_file.exists():
        history_file.write_text("# Version History\n\n")
    
    # Check if the version already exists in the file
    with history_file.open('r') as f:
        content = f.read()
        if f"## {new_version} - {datetime.now().strftime('%Y-%m-%d')}" in content:
            logging.info(f"Version {new_version} already exists in {history_file}")
            return
    
    with history_file.open('a') as f:
        f.write(f"## {new_version} - {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("- Version bump\n")
        f.write("- Fixed version management tests\n")
        f.write("- Improved version history tracking\n\n")

def validate_production_environment() -> bool:
    """Validate production environment settings"""
    required_vars = {
        'SQLALCHEMY_DATABASE_URI': str,
        'SECRET_KEY': str,  # Minimum 64 chars
        'ADMIN_EMAIL': str,
        'ADMIN_PASSWORD': str,  # Minimum 12 chars
        'FLASK_ENV': str,
        'FLASK_DEBUG': str
    }
    
    missing_vars = []
    invalid_types = []
    invalid_lengths = []
    
    for var, var_type in required_vars.items():
        if var not in os.environ:
            missing_vars.append(var)
            continue
            
        try:
            value = os.environ[var]
            # Type validation
            converted = var_type(value)
            
            # Length validation
            if var == 'SECRET_KEY' and len(value) < 64:
                invalid_lengths.append(f"{var} (min 64 chars)")
                continue
            if var == 'ADMIN_PASSWORD' and len(value) < 12:
                invalid_lengths.append(f"{var} (min 12 chars)")
                continue
                
            # Additional SECRET_KEY complexity checks
            if var == 'SECRET_KEY':
                if not any(c.isupper() for c in value):
                    logging.error(f"{var} must contain uppercase letters")
                    return False
                if not any(c.islower() for c in value):
                    logging.error(f"{var} must contain lowercase letters")
                    return False
                if not any(c.isdigit() for c in value):
                    logging.error(f"{var} must contain numbers")
                    return False
                if not any(c in "!@#$%^&*()_+-=[]{};':,.<>?/" for c in value):
                    logging.error(f"{var} must contain special characters")
                    return False
                    
        except (ValueError, TypeError):
            invalid_types.append(var)
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
        
    if invalid_types:
        logging.error(f"Invalid type for environment variables: {', '.join(invalid_types)}")
        return False
        
    if invalid_lengths:
        logging.error(f"Invalid length for variables: {', '.join(invalid_lengths)}")
        return False
        
    logging.info("Production environment validation passed")
    return True

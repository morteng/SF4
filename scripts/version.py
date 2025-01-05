import subprocess
import re
import sqlite3
import logging
import time
import os
from typing import Optional, Tuple
from datetime import datetime
from pathlib import Path

__version__ = "0.2.0"  # Enhanced version management

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('version_management.log'),
        logging.StreamHandler()
    ]
)

def validate_db_connection(db_path: str) -> bool:
    """Validate database connection with retry logic and detailed logging"""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            logging.info(f"Database connection successful to {db_path}")
            return True
        except sqlite3.Error as e:
            if attempt == max_retries - 1:
                logging.error(f"Database connection failed after {max_retries} attempts: {str(e)}")
                return False
            logging.warning(f"Database connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
            time.sleep(retry_delay)

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

def validate_version(version: str) -> bool:
    """Validate version string format including build metadata"""
    return bool(re.match(r"^\d+\.\d+\.\d+(-[a-z]+(\.\d+)?)?(\+[a-z0-9]+(\.[a-z0-9]+)*)?$", version))

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

def bump_version(version_type="patch") -> str:
    """Bump the version number and return the new version string"""
    if version_type not in ["major", "minor", "patch"]:
        raise ValueError("version_type must be 'major', 'minor' or 'patch'")

    major, minor, patch, suffix = parse_version(__version__)

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
    return new_version

def update_version_file(new_version: str) -> None:
    """Update the __version__ in the version.py file"""
    with open(__file__, 'r') as f:
        lines = f.readlines()
    with open(__file__, 'w') as f:
        for line in lines:
            if line.startswith("__version__"):
                f.write(f'__version__ = "{new_version}"\n')
            else:
                f.write(line)

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

def validate_version_file(file_path: Optional[str] = None) -> bool:
    """Validate version file integrity
    
    Args:
        file_path: Optional path to version file. If None, uses current file.
    
    Returns:
        bool: True if version file is valid, False otherwise
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

def create_version_history(new_version: str) -> None:
    """Create version history file"""
    history_file = Path('VERSION_HISTORY.md')
    if not history_file.exists():
        history_file.write_text("# Version History\n\n")
    
    with history_file.open('a') as f:
        f.write(f"## {new_version} - {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("- Initial release\n\n")

def create_db_backup(db_path: str) -> bool:
    """Create a timestamped backup of the database"""
    try:
        backup_path = Path(db_path).with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        conn = sqlite3.connect(db_path)
        with conn:
            conn.execute(f"VACUUM INTO '{backup_path}'")
        logging.info(f"Database backup created at: {backup_path}")
        return True
    except sqlite3.Error as e:
        logging.error(f"Database backup failed: {str(e)}")
        return False

def validate_production_environment() -> bool:
    """Validate production environment settings
    
    Returns:
        bool: True if all required environment variables are present and valid, False otherwise
    """
    required_vars = {
        'DATABASE_URL': str,
        'SECRET_KEY': str,
        'ADMIN_EMAIL': str
    }
    
    missing_vars = []
    invalid_types = []
    
    for var, var_type in required_vars.items():
        if var not in os.environ:
            missing_vars.append(var)
        elif not isinstance(os.environ[var], var_type):
            try:
                var_type(os.environ[var])
            except (ValueError, TypeError):
                invalid_types.append(var)
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
        
    if invalid_types:
        logging.error(f"Invalid type for environment variables: {', '.join(invalid_types)}")
        return False
        
    logging.info("Production environment validation passed")
    return True

def verify_logging_configuration() -> bool:
    """Verify logging configuration is working correctly
    
    Returns:
        bool: True if logging is configured properly, False otherwise
    """
    try:
        # Test all logging levels
        logging.debug("Debug message test")
        logging.info("Info message test")
        logging.warning("Warning message test")
        logging.error("Error message test")
        logging.critical("Critical message test")
        
        # Verify log file was created and contains messages
        if not os.path.exists('version_management.log'):
            return False
            
        with open('version_management.log') as f:
            content = f.read()
            if not all(level in content for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']):
                return False
                
        return True
    except Exception as e:
        logging.error(f"Logging configuration verification failed: {str(e)}")
        return False

import subprocess
import re
import sqlite3
from typing import Optional, Tuple
from datetime import datetime

__version__ = "0.1.0"  # Initial version

def validate_db_connection(db_path: str) -> bool:
    """Validate database connection"""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
        return True
    except sqlite3.Error:
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

def validate_version(version: str) -> bool:
    """Validate version string format"""
    return bool(re.match(r"^\d+\.\d+\.\d+(-[a-z]+\.\d+)?$", version))

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
    """Bump the version number and create appropriate git branch"""
    if version_type not in ["major", "minor", "patch"]:
        raise ValueError("version_type must be 'major', 'minor' or 'patch'")
    
    major, minor, patch, suffix = parse_version(__version__)
    
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
        branch_type = "release"
    elif version_type == "minor":
        minor += 1
        patch = 0
        branch_type = "feature"
    else:
        patch += 1
        branch_type = "bugfix"
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Create appropriate git branch
    branch_name = f"{branch_type}/v{new_version}"
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        # Update version in this file
        with open(__file__, 'r') as f:
            lines = f.readlines()
        with open(__file__, 'w') as f:
            for line in lines:
                if line.startswith("__version__"):
                    f.write(f'__version__ = "{new_version}"\n')
                else:
                    f.write(line)
    except subprocess.CalledProcessError as e:
        print(f"Error creating branch: {e}")
        raise
    
    return new_version

def push_to_github(branch_name: str, commit_message: str) -> bool:
    """Push changes to GitHub with proper validation"""
    try:
        # Verify branch exists
        subprocess.run(["git", "rev-parse", "--verify", branch_name], check=True)
        
        # Stage changes
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit with message
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push to remote
        subprocess.run(["git", "push", "origin", branch_name], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        return False

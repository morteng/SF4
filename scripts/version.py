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


import subprocess
from typing import Optional

__version__ = "0.1.0"  # Initial version

def get_version():
    """Get the current project version"""
    return __version__

def bump_version(version_type="patch"):
    """Bump the version number and create appropriate git branch
    Args:
        version_type (str): Type of version bump - 'major', 'minor', or 'patch'
    Returns:
        str: New version string
    """
    major, minor, patch = map(int, __version__.split('.'))
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
    subprocess.run(["git", "checkout", "-b", branch_name])
    
    return new_version

def push_to_github(branch_name: str, commit_message: str) -> bool:
    """Push changes to GitHub
    Args:
        branch_name: Name of branch to push
        commit_message: Commit message
    Returns:
        bool: True if successful
    """
    try:
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", commit_message])
        subprocess.run(["git", "push", "origin", branch_name])
        return True
    except Exception as e:
        print(f"Error pushing to GitHub: {e}")
        return False

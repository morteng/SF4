import sys
from datetime import datetime

def update_release_notes():
    """Update release notes with current version information"""
    try:
        with open('RELEASE_NOTES.md', 'a') as f:
            f.write(f"\n## Version 0.2.0 - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("- Fixed version management CLI arguments\n")
            f.write("- Added proper error handling for archive-logs\n")
            f.write("- Implemented version history tracking\n")
        return True
    except Exception as e:
        print(f"Failed to update release notes: {str(e)}")
        return False

def update_version_history():
    """Update version history file"""
    try:
        with open('VERSION_HISTORY.md', 'a') as f:
            f.write(f"\n## 0.2.0 - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("- Initial production release\n")
            f.write("- Fixed version management CLI arguments\n")
            f.write("- Added proper error handling for archive-logs\n")
            f.write("- Implemented version history tracking\n")
        return True
    except Exception as e:
        print(f"Failed to update version history: {str(e)}")
        return False

def finalize_docs():
    """Finalize all documentation updates"""
    if not update_release_notes():
        return False
    if not update_version_history():
        return False
    return True

if __name__ == "__main__":
    if finalize_docs():
        print("Documentation finalized successfully")
        sys.exit(0)
    else:
        print("Documentation finalization failed")
        sys.exit(1)

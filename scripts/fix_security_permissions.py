import os
import stat
import logging
from pathlib import Path

def fix_permissions():
    """Fix security permissions for sensitive files"""
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Files to secure
        sensitive_files = [
            '.env',
            'instance/site.db',
            'migrations/'
        ]
        
        # Set secure permissions
        for file in sensitive_files:
            path = Path(file)
            if path.exists():
                # Remove world-readable/writable permissions
                current_mode = path.stat().st_mode
                new_mode = current_mode & ~stat.S_IWOTH & ~stat.S_IROTH
                path.chmod(new_mode)
                logger.info(f"Fixed permissions for {file}: {oct(new_mode)}")
                
        return True
    except Exception as e:
        logger.error(f"Failed to fix permissions: {str(e)}")
        return False

if __name__ == "__main__":
    if fix_permissions():
        print("Security permissions fixed successfully")
        exit(0)
    else:
        print("Failed to fix security permissions")
        exit(1)

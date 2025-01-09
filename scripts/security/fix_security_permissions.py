import os
import stat
import logging
from pathlib import Path

def fix_permissions():
    """Fix security permissions for sensitive files with strict mode"""
    try:
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Ensure debug mode is disabled
        os.environ['FLASK_DEBUG'] = '0'
        
        # Files to secure with target permissions
        sensitive_files = {
            '.env': 0o600,
            'instance/site.db': 0o600,
            'migrations/': 0o700,
            'logs/': 0o750,
            'scripts/': 0o750
        }

        # Ensure files exist before setting permissions
        for file, target_mode in sensitive_files.items():
            path = Path(file)
            if not path.exists():
                logger.warning(f"File not found: {file}")
                continue
                
            # Remove existing permissions first
            path.chmod(0o777)
            # Set new permissions
            path.chmod(target_mode)
            # Verify
            actual_mode = path.stat().st_mode & 0o777
            if actual_mode != target_mode:
                logger.error(f"Failed to set permissions for {file}: {oct(actual_mode)} (expected {oct(target_mode)})")
                return False
            logger.info(f"Fixed permissions for {file}: {oct(target_mode)}")
                
        return True

        # Ensure files exist before setting permissions
        for file, target_mode in sensitive_files.items():
            path = Path(file)
            if not path.exists():
                logger.warning(f"File not found: {file}")
                continue
        
        # Set secure permissions
        for file, target_mode in sensitive_files.items():
            path = Path(file)
            if path.exists():
                # Set exact permissions
                path.chmod(target_mode)
                # Verify
                actual_mode = path.stat().st_mode & 0o777
                if actual_mode != target_mode:
                    logger.error(f"Failed to set permissions for {file}: {oct(actual_mode)} (expected {oct(target_mode)})")
                    return False
                logger.info(f"Fixed permissions for {file}: {oct(target_mode)}")
                
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

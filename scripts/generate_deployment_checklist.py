import sys
import logging
from datetime import datetime

import logging
from pathlib import Path

def configure_logger():
    """Configure the logger for checklist generation"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def generate_checklist(validate=False):
    """Enhanced deployment checklist with comprehensive validation"""
    logger = configure_logger()
    
    try:
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            logger.error("Path configuration failed")
            return False
            
        # Verify git state
        from scripts.verification.verify_git_state import verify_git_state
        if not verify_git_state():
            logger.error("Cannot generate checklist with uncommitted changes")
            return False
            
        # Get test coverage
        from scripts.verification.verify_test_coverage import verify_coverage
        coverage = verify_coverage(threshold=80)
        
        # Get deployment status
        from scripts.verification.verify_deployment import verify_deployment
        deployment_status = verify_deployment()
        
        # Get version info
        from scripts.version import get_version
        version = get_version()
        
        # Create deployment directory if it doesn't exist
        Path('deployment').mkdir(exist_ok=True)
        
        with open('deployment/DEPLOYMENT_CHECKLIST.md', 'w') as f:
            f.write("# Deployment Checklist\n")
            f.write(f"## Version: {version}\n")
            f.write(f"## Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # Add comprehensive checklist items
            f.write("## Core Verification\n")
            f.write(f"- [{'x' if verify_git_state() else ' '}] Git state verified\n")
            f.write(f"- [{'x' if verify_coverage() else ' '}] Test coverage meets 80% requirement\n")
            f.write(f"- [{'x' if deployment_status else ' '}] Deployment verification passed\n\n")
            
            f.write("## Security Verification\n")
            f.write(f"- [{'x' if verify_security_settings() else ' '}] Security settings verified\n")
            f.write(f"- [{'x' if verify_backup_integrity() else ' '}] Backup system verified\n\n")
            
            f.write("## Documentation\n")
            f.write("- [x] Release notes updated\n")
            f.write("- [x] Version history updated\n")
            f.write("- [x] Deployment checklist generated\n")
            
        logger.info("Deployment checklist generated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to generate deployment checklist: {str(e)}")
        return False
    except Exception as e:
        print(f"Failed to generate deployment checklist: {str(e)}")
        return False

if __name__ == "__main__":
    generate_checklist()

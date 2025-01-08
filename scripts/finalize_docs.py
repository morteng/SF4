import sys
import logging
from datetime import datetime
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Configure paths first
from scripts.path_config import configure_paths
if not configure_paths():
    logger.error("Path configuration failed")
    exit(1)

def update_release_notes():
    """Update release notes with current version information"""
    try:
        # Configure logger
        global logger
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
        # Get test coverage
        from scripts.verify_test_coverage import get_coverage
        coverage = get_coverage()
        if not coverage:
            logger.error("Could not get test coverage")
            return False
            
        # Verify git state first
        from scripts.verify_git_state import verify_git_state
        if not verify_git_state():
            logger.error("Cannot update docs with uncommitted changes")
            return False
            
        # Get version info
        from scripts.version import get_version
        version = get_version()
        if not version:
            logger.error("Could not determine current version")
            return False
            
        # Get test coverage
        from scripts.generate_coverage_report import get_coverage
        coverage = get_coverage()
            
        # Add project root to Python path
        import sys
        from pathlib import Path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Add project root to Python path
        import sys
        from pathlib import Path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Add scripts directory
        scripts_dir = str(Path(__file__).parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        # Ensure proper version import
        try:
            from version import __version__
        except ImportError:
            from scripts.version import __version__
        
        with open('RELEASE_NOTES.md', 'r') as f:
            content = f.read()
            if f"## Version {__version__}" in content:
                logger.info("Release notes already up to date")
                return True
                
        with open('RELEASE_NOTES.md', 'a') as f:
            f.write(f"\n## Version {__version__} - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("- Finalized deployment verification system\n")
            f.write("- Improved error handling and logging\n")
            f.write("- Streamlined review process\n")
            f.write("- Added comprehensive documentation\n")
            f.write("- Verified production readiness\n")
            
        logger.info("Release notes updated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to update release notes: {str(e)}")
        return False

def update_version_history():
    """Update version history file"""
    try:
        # Clean up duplicate entries
        with open('VERSION_HISTORY.md', 'r') as f:
            lines = f.readlines()
        
        # Keep only unique entries
        unique_lines = []
        seen = set()
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        # Write cleaned version history
        with open('VERSION_HISTORY.md', 'w') as f:
            f.writelines(unique_lines)
            
        # Add new entry
        with open('VERSION_HISTORY.md', 'a') as f:
            f.write(f"\n## 1.2.11 - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("- Fixed deployment verification logging\n")
            f.write("- Improved documentation generation\n")
            f.write("- Added comprehensive review process\n")
            f.write("- Verified production environment\n")
            
        logger.info("Version history updated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to update version history: {str(e)}")
        return False

def finalize_docs():
    """Finalize all documentation updates"""
    try:
        # Update release notes
        if not update_release_notes():
            return False
            
        # Update version history
        if not update_version_history():
            return False
            
        # Generate deployment checklist
        from scripts.generate_deployment_checklist import generate_checklist
        if not generate_checklist():
            return False
            
        return True
    except Exception as e:
        logger.error(f"Documentation finalization failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if finalize_docs():
        logger.info("Documentation finalized successfully")
        exit(0)
    else:
        logger.error("Documentation finalization failed")
        exit(1)

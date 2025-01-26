import subprocess
import logging
from pathlib import Path
import sys

def configure_logging():
    """Configure logging for commit script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/commit.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def commit_changes(message, push=False):
    """Final deployment commit with force add"""
    # Force add all changes
    subprocess.run(['git', 'add', '-A'], check=True)
    logger = configure_logging()
    # Normalize paths for Windows
    from pathlib import Path
    Path('logs/commit.log').parent.mkdir(parents=True, exist_ok=True)
    try:
        # Add project root to Python path
        import sys
        from pathlib import Path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Configure paths first
        from scripts.path_config import configure_paths
        if not configure_paths():
            raise RuntimeError("Failed to configure paths")
            
        # Verify git status first
        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        if not status.stdout.strip():
            logger.info("No changes to commit")
            return True
            
        # Stage all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit with message
        # Force add all changes and push
        subprocess.run(['git', 'add', '-A'], check=True)
        subprocess.run(['git', 'commit', '-m', message], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        # Push changes if requested
        if push:
            subprocess.run(['git', 'push'], check=True)
            logger.info(f"Successfully committed and pushed changes: {message}")
        else:
            logger.info(f"Successfully committed changes: {message}")
            
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Commit failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during commit: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == '--message':
        message = sys.argv[2]
        if commit_changes(message):
            exit(0)
    exit(1)

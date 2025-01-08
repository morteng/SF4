import logging
from pathlib import Path

def verify_review():
    """Verify all review steps are complete"""
    logger = logging.getLogger(__name__)
    
    try:
        # Verify required files
        required_files = [
            'DEPLOYMENT_CHECKLIST.md',
            'RELEASE_NOTES.md',
            'VERSION_HISTORY.md',
            'requirements.txt',
            'migrations/alembic.ini'
        ]
        
        for file in required_files:
            if not Path(file).exists():
                logger.error(f"Missing required file: {file}")
                return False
                
        # Verify backups
        backup_files = list(Path('backups').glob('*.db'))
        if not backup_files:
            logger.error("No database backups found")
            return False
            
        # Verify logs
        log_files = list(Path('logs').glob('*.log'))
        if not log_files:
            logger.error("No log files found")
            return False
            
        # Verify test coverage
        from scripts.verify_test_coverage import verify_coverage
        if not verify_coverage(threshold=80):
            logger.error("Test coverage below 80%")
            return False
            
        # Verify test cleanup
        from scripts.verify_test_cleanup import verify_test_cleanup
        if not verify_test_cleanup():
            logger.error("Test cleanup failed")
            return False
            
        logger.info("All review steps completed successfully")
        return True
        
        for file in required_files:
            if not Path(file).exists():
                logger.error(f"Missing required file: {file}")
                return False
                
        # Check deployment checklist is complete
        with open('DEPLOYMENT_CHECKLIST.md') as f:
            if "[ ]" in f.read():
                logger.error("Deployment checklist has incomplete items")
                return False
                
        logger.info("All review steps completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Review verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_review():
        exit(0)
    else:
        exit(1)

import logging
from pathlib import Path

def verify_review():
    """Verify all review steps are complete"""
    logger = logging.getLogger(__name__)
    
    try:
        # Check required files exist
        required_files = [
            'DEPLOYMENT_CHECKLIST.md',
            'RELEASE_NOTES.md',
            'VERSION_HISTORY.md',
            'scripts/REQUESTS.txt'
        ]
        
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

import sys
import logging
from pathlib import Path

def verify_all():
    """Perform final verification before deployment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Add project root to Python path
        root_dir = Path(__file__).parent.parent
        sys.path.append(str(root_dir))
        
        # Import verification modules
        from scripts.verify_production import verify_production
        from scripts.verify_deployment import verify_deployment
        from scripts.verify_test_db import verify_test_db
        from scripts.check_coverage import check_coverage
        
        # Run verifications
        if not verify_production():
            logger.error("Production verification failed")
            return False
            
        if not verify_deployment():
            logger.error("Deployment verification failed")
            return False
            
        if not verify_test_db():
            logger.error("Test database verification failed")
            return False
            
        if not check_coverage():
            logger.error("Test coverage verification failed")
            return False
            
        logger.info("All verifications passed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Final verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if verify_all():
        exit(0)
    else:
        exit(1)

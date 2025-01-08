import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def verify_deployment_requirements():
    """Verify all deployment requirements are met"""
    try:
        # Import verification modules
        from scripts.verify_git_state import verify_git_state
        from scripts.verify_db_connection import verify_db_connection
        from scripts.verify_test_coverage import verify_coverage
        from scripts.verify_deployment import verify_deployment
        
        # Run verification checks
        checks = [
            ("Git state", verify_git_state),
            ("Database connection", verify_db_connection),
            ("Test coverage", verify_coverage),
            ("Deployment configuration", verify_deployment)
        ]
        
        for check_name, check_fn in checks:
            if not check_fn():
                logger.error(f"{check_name} verification failed")
                return False
                
        logger.info("All deployment requirements verified")
        return True
        
    except Exception as e:
        logger.error(f"Deployment verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_deployment_requirements():
        print("Deployment requirements verified")
        exit(0)
    else:
        print("Deployment verification failed")
        exit(1)

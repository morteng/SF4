import os
import logging
from pathlib import Path

def configure_logger():
    """Configure logger for feedback verification"""
    logger = logging.getLogger('feedback')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_feedback_setup(check_surveys=False, check_analytics=False):
    """Verify user feedback collection setup"""
    logger = configure_logger()
    
    try:
        # Verify required environment variables
        required_vars = [
            'FEEDBACK_ENABLED',
            'SURVEY_INTERVAL',
            'ANALYTICS_ENABLED'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing feedback environment variables: {', '.join(missing_vars)}")
            return False
            
        # Verify survey configuration
        if check_surveys:
            survey_dir = Path('surveys')
            if not survey_dir.exists():
                logger.info("Creating survey directory structure")
                try:
                    survey_dir.mkdir(parents=True, exist_ok=True)
                    (survey_dir / 'template.json').write_text('{}')
                    (survey_dir / 'responses.db').touch()
                    logger.info("Created default survey files")
                except Exception as e:
                    logger.error(f"Failed to create survey files: {str(e)}")
                    return False
                
        # Verify analytics configuration
        if check_analytics:
            if not os.getenv('ANALYTICS_ENDPOINT'):
                logger.error("Missing ANALYTICS_ENDPOINT")
                return False
                
        logger.info("Feedback setup verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Feedback verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_feedback_setup():
        print("Feedback verification passed")
        exit(0)
    else:
        print("Feedback verification failed")
        exit(1)

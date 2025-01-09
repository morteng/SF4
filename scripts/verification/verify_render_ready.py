import os
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

def verify_render_environment():
    """Verify all required Render environment variables are set"""
    required_vars = [
        'RENDER_API_KEY',
        'RENDER_SERVICE_ID',
        'DEPLOYMENT_ENV',
        'BACKUP_RETENTION_DAYS'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required Render variables: {', '.join(missing_vars)}")
        return False
        
    # Verify API key format
    api_key = os.getenv('RENDER_API_KEY')
    if not api_key or len(api_key) < 64:
        logger.error("RENDER_API_KEY must be at least 64 characters")
        return False
        
    # Verify service ID format
    service_id = os.getenv('RENDER_SERVICE_ID')
    if not service_id or len(service_id) < 32:
        logger.error("RENDER_SERVICE_ID must be at least 32 characters")
        return False
        
    return True

def verify_render_api():
    """Verify Render API connectivity"""
    try:
        response = requests.get(
            "https://api.render.com/v1/services",
            headers={"Authorization": f"Bearer {os.getenv('RENDER_API_KEY')}"},
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Render API connection failed: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Render API verification failed: {str(e)}")
        return False

def verify_render_ready():
    """Main verification function"""
    if not verify_render_environment():
        return False
        
    if not verify_render_api():
        return False
        
    logger.info("Render environment is ready for deployment")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if verify_render_ready():
        exit(0)
    else:
        exit(1)

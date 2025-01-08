import os
import logging
import requests
from pathlib import Path

def configure_logger():
    """Configure consistent logging for API client"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

class RenderClient:
    def __init__(self):
        self.logger = configure_logger()
        self.api_key = os.getenv('RENDER_API_KEY')
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

    def verify_service(self, service_id):
        """Verify Render service exists and is accessible"""
        try:
            url = f"{self.base_url}/services/{service_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("Render service verified successfully")
                return True
                
            self.logger.error(f"Render service verification failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.logger.error(f"Render API connection failed: {str(e)}")
            return False

    def trigger_deployment(self, service_id):
        """Trigger a new deployment for the service"""
        try:
            url = f"{self.base_url}/services/{service_id}/deploys"
            response = requests.post(url, headers=self.headers, timeout=10)
            
            if response.status_code == 201:
                self.logger.info("Deployment triggered successfully")
                return True
                
            self.logger.error(f"Deployment trigger failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.logger.error(f"Deployment trigger failed: {str(e)}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = RenderClient()
    if client.verify_service(os.getenv('RENDER_SERVICE_ID')):
        print("Render service verification passed")
        exit(0)
    else:
        print("Render service verification failed")
        exit(1)

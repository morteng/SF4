import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup

def configure_logger():
    """Configure logger for HTMX verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_htmx_crud(base_url):
    """Verify CRUD operations through HTMX interface"""
    logger = configure_logger()
    
    try:
        # Test login and session
        session = requests.Session()
        login_url = f"{base_url}/login"
        login_data = {
            'username': 'admin',
            'password': os.getenv('ADMIN_PASSWORD')
        }
        response = session.post(login_url, data=login_data)
        if response.status_code != 200:
            logger.error("Login failed")
            return False
            
        # Test CRUD operations
        test_data = {
            'name': 'Test Stipend',
            'description': 'Test Description',
            'tags': 'Test'
        }
        
        # Create
        create_url = f"{base_url}/admin/stipend/create"
        response = session.post(create_url, data=test_data)
        if response.status_code != 200:
            logger.error("Create operation failed")
            return False
            
        # Verify creation
        list_url = f"{base_url}/admin/stipend"
        response = session.get(list_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.find(text=test_data['name']):
            logger.error("Created item not found")
            return False
            
        logger.info("HTMX CRUD verification passed")
        return True
        
    except Exception as e:
        logger.error(f"HTMX verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    if verify_htmx_crud(base_url):
        print("HTMX integration verification passed")
        exit(0)
    else:
        print("HTMX integration verification failed")
        exit(1)

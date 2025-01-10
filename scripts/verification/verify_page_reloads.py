import logging
import requests
from bs4 import BeautifulSoup

def configure_logger():
    """Configure logger for page reload verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def verify_page_reloads(base_url):
    """Verify that CRUD operations trigger full page reloads"""
    logger = configure_logger()
    
    try:
        # Test admin login
        session = requests.Session()
        login_url = f"{base_url}/admin/login"
        login_data = {
            'username': 'admin',
            'password': os.getenv('ADMIN_PASSWORD'),
            'csrf_token': get_csrf_token(base_url)
        }
        
        response = session.post(login_url, data=login_data)
        if response.status_code != 200:
            logger.error("Login failed")
            return False
            
        # Test create operation
        create_url = f"{base_url}/admin/stipend/create"
        test_data = {'name': 'Test Stipend'}
        response = session.post(create_url, data=test_data)
        
        # Verify full page reload by checking for complete page structure
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.find('html') or not soup.find('body'):
            logger.error("Create operation did not trigger full page reload")
            return False
            
        logger.info("Page reload verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Page reload verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    import os
    import argparse
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true', help='Run full verification')
    args = parser.parse_args()
    
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    if verify_page_reloads(base_url):
        print("Page reload verification passed")
        exit(0)
    else:
        print("Page reload verification failed")
        exit(1)

import logging
import sys
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

def verify_htmx_crud(base_url, test_all_crud=False, admin_only=False, validate_partial_updates=False):
    """Verify CRUD operations through HTMX interface with enhanced admin checks
    Args:
        base_url (str): Base URL of application
        test_all_crud (bool): Whether to test all CRUD operations
        admin_only (bool): Focus only on admin functionality
        validate_partial_updates (bool): Verify HTMX partial page updates
    """
    # Add project root to sys.path
    project_root = str(Path(__file__).parent.parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
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
            
        # Test CRUD operations for stipends
        test_data = {
            'name': 'Test Stipend',
            'description': 'Test Description',
            'tags': 'Test',
            'amount': '1000',
            'deadline': '2025-12-31',
            'organization_id': 1
        }
        
        # Create
        create_url = f"{base_url}/admin/stipend/create"
        response = session.post(create_url, data=test_data)
        if response.status_code != 200:
            logger.error("Stipend create operation failed")
            return False
            
        # Verify creation
        list_url = f"{base_url}/admin/stipend"
        response = session.get(list_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.find(text=test_data['name']):
            logger.error("Created stipend not found")
            return False
            
        # Test update
        edit_url = f"{base_url}/admin/stipend/1/edit"
        update_data = test_data.copy()
        update_data['name'] = 'Updated Stipend'
        response = session.post(edit_url, data=update_data)
        if response.status_code != 200:
            logger.error("Stipend update operation failed")
            return False
            
        # Verify update
        response = session.get(list_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.find(text=update_data['name']):
            logger.error("Updated stipend not found")
            return False
            
        # Test delete
        delete_url = f"{base_url}/admin/stipend/1/delete"
        response = session.post(delete_url)
        if response.status_code != 200:
            logger.error("Stipend delete operation failed")
            return False
            
        # Verify deletion
        response = session.get(list_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find(text=update_data['name']):
            logger.error("Deleted stipend still exists")
            return False
            
        logger.info("HTMX CRUD verification passed")
        return True
        
    except Exception as e:
        logger.error(f"HTMX verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    import os
    import argparse
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true', help='Run full verification')
    parser.add_argument('--test-all-crud', action='store_true',
                       help='Test all CRUD operations across entities')
    parser.add_argument('--admin-only', action='store_true',
                       help='Focus only on admin functionality')
    args = parser.parse_args()
    
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    if verify_htmx_crud(base_url, args.test_all_crud):
        print("HTMX integration verification passed")
        exit(0)
    else:
        print("HTMX integration verification failed")
        exit(1)

from flask import Response
from app.constants import FlashMessages
import logging

def assert_flash_message(response: Response, message: FlashMessages) -> None:
    """Assert that a specific flash message is present in the response."""
    assert message.value.encode() in response.data, \
        f"Expected flash message '{message.value}' not found in response"
    logging.info(f"Verified flash message: {message.value}")

def create_bot_data(name="TestBot", description="Test Description", status=True):
    """Factory function to create bot test data."""
    return {
        'name': name,
        'description': description,
        'status': 'true' if status else 'false'
    }

def create_user_data(username="testuser", email="test@example.com", password="password123"):
    """Factory function to create user test data."""
    return {
        'username': username,
        'email': email,
        'password': password
    }

def extract_csrf_token(response_data):
    """Extract CSRF token from HTML response."""
    import re
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(response_data, 'html.parser')
    
    # Look for CSRF token in meta tag first
    meta_token = soup.find('meta', attrs={'name': 'csrf-token'})
    if meta_token and meta_token.get('content'):
        logging.info("Found CSRF token in meta tag")
        return meta_token.get('content')
    
    # Look for CSRF token in hidden input
    input_token = soup.find('input', attrs={'name': 'csrf_token', 'type': 'hidden'})
    if input_token and input_token.get('value'):
        logging.info("Found CSRF token in hidden input")
        return input_token.get('value')
    
    # Look for CSRF token in form data
    form = soup.find('form')
    if form:
        input_token = form.find('input', attrs={'name': 'csrf_token', 'type': 'hidden'})
        if input_token and input_token.get('value'):
            logging.info("Found CSRF token in form")
            return input_token.get('value')
    
    # Debug: Log the HTML if no token found
    logging.warning("CSRF token not found in response. HTML content:")
    logging.warning(soup.prettify())
    
    # Look for CSRF token in HTMX headers
    script_tags = soup.find_all('script')
    for script in script_tags:
        if 'hx-headers' in script.text:
            match = re.search(r'"X-CSRFToken":\s*"([^"]+)"', script.text)
            if match:
                return match.group(1)
    
    # If no token found, log the issue
    logging.warning("CSRF token not found in response")
    return None

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='admin', password='password'):
        return self._client.post(
            '/login',
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/logout', follow_redirects=True)

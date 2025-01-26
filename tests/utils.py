from flask import Response
from app.constants import FlashMessages
import logging
from bs4 import BeautifulSoup
import re

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
    """Extract CSRF token from HTML response using regex."""
    decoded_data = response_data.decode()
    match = re.search(r'name="csrf_token"[^>]+value="([^"]+)"', decoded_data)
    if match:
        return match.group(1)
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

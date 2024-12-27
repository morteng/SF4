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

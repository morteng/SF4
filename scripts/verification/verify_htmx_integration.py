import logging
import sys
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import argparse

def get_csrf_token(base_url):
    """Get CSRF token from login page"""
    try:
        response = requests.get(f"{base_url}/admin/login")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            return csrf_input.get('value')
        return ''
    except Exception as e:
        logging.error(f"Failed to get CSRF token: {str(e)}")
        return ''

def configure_logger():
    """Configure logger for HTMX verification"""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
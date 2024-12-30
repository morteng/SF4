import pytest
from flask import url_for

def test_login_redirect(client):
    """Test that login redirects to the correct page after successful authentication"""
    # Test data
    test_user = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    
    # Make login request
    response = client.post(url_for('public.login'), data=test_user, follow_redirects=False)
    
    # Verify redirect status code and location
    assert response.status_code == 302
    assert response.location == url_for('public.index', _external=True)

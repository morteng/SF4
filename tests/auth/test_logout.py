import pytest
from flask import url_for

def test_logout(logged_in_client):
    """Test logout functionality"""
    response = logged_in_client.get(url_for('public.logout'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Logged out successfully" in response.data
    with logged_in_client.session_transaction() as session:
        assert '_user_id' not in session

import pytest
from flask import Flask, jsonify
from app.utils import admin_required
from app.models.user import User

def test_admin_required_decorator(app, client, admin_token):
    """Test the admin_required decorator with valid and invalid auth."""
    
    # Create a test route using the decorator
    @app.route('/test_admin')
    @admin_required 
    def protected_route(admin_user):
        return jsonify({"message": "Access granted"}), 200

    # Test with valid admin token
    response = client.get('/test_admin', 
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json['message'] == "Access granted"

    # Test with invalid token
    response = client.get('/test_admin', 
                         headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401

    # Test with missing token
    response = client.get('/test_admin')
    assert response.status_code == 401

    # Test with malformed Authorization header
    response = client.get('/test_admin', 
                         headers={'Authorization': 'invalid_format'})
    assert response.status_code == 401

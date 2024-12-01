import pytest
from flask import Flask, jsonify
from flask_login import login_required
from app.models.user import User

@pytest.fixture(scope='function')
def app():
    from app import create_app
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(client):
    response = client.post('/admin/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    return response

def test_login_required_decorator(app, client, admin_user):
    """Test the login_required decorator with valid and invalid auth."""
    
    # Create a test route using the decorator
    @app.route('/test_admin')
    @login_required
    def protected_route():
        return jsonify({"message": "Access granted"}), 200

    # Test with valid session cookie (from admin_user fixture)
    response = client.get('/test_admin', headers=admin_user.headers)
    assert response.status_code == 200

    # Test with invalid session cookie
    client.set_cookie('localhost', 'user_id', value='invalid_id')
    response = client.get('/test_admin')
    assert response.status_code == 401

    # Test with missing session cookie
    client.cookie_jar.clear()
    response = client.get('/test_admin')
    assert response.status_code == 401

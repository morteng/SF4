import pytest
from app.utils import init_admin_user  # This is all we need since utils already imports User

def test_init_admin_user(app, session):
    """Test admin user initialization"""
    # First run should create admin
    admin = init_admin_user()
    assert admin is not None
    assert admin.username == 'admin'
    assert admin.is_admin is True
    
    # Second run should return existing admin
    admin2 = init_admin_user()
    assert admin2.id == admin.id

def test_admin_required_decorator(client, admin_token):
    """Test admin_required decorator"""
    # Test without auth header
    response = client.get('/admin/bots/status')
    assert response.status_code == 401
    
    # Test with invalid token
    response = client.get('/admin/bots/status', 
                         headers={'Authorization': 'Bearer invalid'})
    assert response.status_code == 401
    
    # Test with admin user token
    response = client.get('/admin/bots/status', 
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200

def test_admin_required_decorator_non_admin(client):
    """Test admin_required decorator with non-admin user"""
    # Create a non-admin user and generate token
    non_admin_user = User(
        username='non_admin',
        email='non_admin@example.com',
        is_admin=False
    )
    non_admin_user.set_password('non_admin')
    db.session.add(non_admin_user)
    db.session.commit()
    
    token = non_admin_user.generate_auth_token()
    
    # Test with non-admin user token
    response = client.get('/admin/bots/status', 
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403

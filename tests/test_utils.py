import pytest
from app.models.user import User
from app.models.bot import Bot
from app.extensions import db  # Import the db object

@pytest.fixture
def admin_user(app, session):
    """Create test admin user"""
    user = User(
        username='admin_test',
        email='admin@test.com',
        is_admin=True
    )
    user.set_password('test_password')
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def admin_token(admin_user):
    """Generate admin authentication token"""
    return admin_user.generate_auth_token()

@pytest.fixture
def test_bot(session):
    """Create test bot"""
    bot = Bot(
        name='Test Bot',
        description='Test Description',
        status='active'
    )
    session.add(bot)
    session.commit()
    return bot

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

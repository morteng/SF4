from app.models.user import User
from tests.conftest import extract_csrf_token

def test_login(client, db_session, app):
    """Test login flow including CSRF protection"""
    # Create test user
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db_session.add(user)
        db_session.commit()

    # Get login page and extract CSRF token using helper
    login_page = client.get('/login')
    assert login_page.status_code == 200
    
    csrf_token = extract_csrf_token(login_page.data)
    assert csrf_token is not None, "CSRF token not found in login form"
    
    # Submit login with valid credentials and CSRF token
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Verify redirect to home page after successful login
    assert response.status_code == 302
    assert response.location == '/'
    
    # Verify session contains user_id
    with client.session_transaction() as session:
        assert 'user_id' in session
    
    # Verify authenticated users are redirected from login page
    login_redirect = client.get('/login')
    assert login_redirect.status_code == 302
    assert login_redirect.location == '/'  # Should redirect to home page
    
    # Test login with invalid CSRF token
    invalid_response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': 'invalid_token'
    }, follow_redirects=True)
    assert b"CSRF token is invalid" in invalid_response.data

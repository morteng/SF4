def test_login(client):
    """Test login flow including CSRF protection"""
    # First verify we can access login page when not authenticated
    login_page = client.get('/login')
    assert login_page.status_code == 200
    
    # Verify CSRF token is present in the form
    login_html = login_page.data.decode()
    assert 'name="csrf_token"' in login_html
    
    # Extract CSRF token more safely
    csrf_token = None
    if 'name="csrf_token"' in login_html:
        csrf_start = login_html.find('name="csrf_token" value="') + len('name="csrf_token" value="')
        csrf_end = login_html.find('"', csrf_start)
        csrf_token = login_html[csrf_start:csrf_end]
    
    assert csrf_token is not None, "CSRF token not found in login form"
    
    # Submit login with valid credentials and CSRF token
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Verify redirect to home page after successful login
    assert response.status_code == 200
    assert b"Login successful" in response.data
    
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

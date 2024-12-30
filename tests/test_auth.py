def test_login(client):
    # First verify we can access login page when not authenticated
    login_page = client.get('/login')
    assert login_page.status_code == 200
    
    # Extract CSRF token from the form
    csrf_token = login_page.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
    
    # Submit login with valid credentials and CSRF token
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Verify redirect to home page after successful login
    assert response.status_code == 200
    assert b"Welcome" in response.data
    
    # Verify authenticated users are redirected from login page
    login_redirect = client.get('/login')
    assert login_redirect.status_code == 302
    assert login_redirect.location == '/'  # Should redirect to home page

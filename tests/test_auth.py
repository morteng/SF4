def test_login(client):
    # First get the login page to retrieve CSRF token
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

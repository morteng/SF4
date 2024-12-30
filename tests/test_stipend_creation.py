def test_create_stipend_with_invalid_characters(client):
    """Test stipend creation with invalid characters in name"""
    # First get the CSRF token from the form page
    form_page = client.get('/admin/stipends/create')
    csrf_token = form_page.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

    # Submit form with invalid characters and CSRF token
    response = client.post('/admin/stipends/create', data={
        'name': 'Invalid@Name!',
        'summary': 'Valid summary',
        'description': 'Valid description',
        'application_deadline': '2024-12-31',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Should redirect and show error in flash messages
    assert response.status_code == 200  # After following redirect
    assert b'Invalid characters in name' in response.data

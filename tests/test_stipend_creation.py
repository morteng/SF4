def test_create_stipend_with_invalid_characters(client):
    # First get the CSRF token from the form page
    form_page = client.get('/admin/stipends/create')
    csrf_token = form_page.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
    
    # Submit form with invalid characters and CSRF token
    response = client.post('/admin/stipends/create', data={
        'name': 'Invalid@Name!',
        'description': 'Test description',
        'application_deadline': '2024-12-31',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Check for redirect and flash message
    assert response.status_code == 200  # Because of follow_redirects=True
    assert b'Invalid characters in name' in response.data

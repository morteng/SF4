from flask import url_for

def test_create_stipend_with_invalid_open_for_applications(client, admin_user):
    """Test creating a stipend with invalid open_for_applications value"""
    login(client, admin_user.username, 'password')
    
    # First get the CSRF token
    get_response = client.get(url_for('admin.admin_stipend.create'))
    csrf_token = get_response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
    
    response = client.post(
        url_for('admin.admin_stipend.create'),
        data={
            'name': 'Test Stipend',
            'open_for_applications': 'invalid',
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    
    # Expect form validation to fail with 400 status
    assert response.status_code == 400
    # Verify error message is present
    assert b'Invalid boolean value' in response.data

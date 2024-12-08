import pytest
from flask_wtf.csrf import generate_csrf
from flask import url_for

@pytest.mark.usefixtures('app', 'client', 'admin_user')
def test_dashboard_data(client, admin_user):
    # Generate CSRF token
    csrf_token = generate_csrf()

    # Log in the admin user
    response = client.post(url_for('public.login'), data={
        'username': admin_user.username,
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200

    # Access the dashboard route
    response = client.get(url_for('admin.dashboard'))
    
    assert response.status_code == 200
    assert b'Stipend Count:' in response.data
    assert b'Recent Bot Logs:' in response.data

    # Ensure current_user is set correctly
    with client.session_transaction() as sess:
        user_id = sess.get('_user_id')
        assert user_id is not None
        assert int(user_id) == admin_user.id

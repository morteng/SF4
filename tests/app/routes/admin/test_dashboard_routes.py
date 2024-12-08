import pytest
from flask import url_for, session

@pytest.mark.usefixtures('app', 'client', 'admin_user')
def test_dashboard_data(client, admin_user):
    # Push an application context
    with client.application.app_context():
        # First, make a GET request to establish a request context
        client.get(url_for('public.login'))

        # Manually set CSRF token in session for testing purposes
        with client.session_transaction() as sess:
            sess['csrf_token'] = 'test_csrf_token'

        # Log in the admin user
        response = client.post(url_for('public.login'), data={
            'username': admin_user.username,
            'password': 'password123',
            'csrf_token': 'test_csrf_token'
        }, follow_redirects=True)
        
        assert response.status_code == 200

        # Access the dashboard route
        response = client.get(url_for('admin.dashboard.dashboard'))
        
        assert response.status_code == 200
        assert b'Stipend Count:' in response.data
        assert b'Recent Bot Logs:' in response.data

        # Ensure current_user is set correctly
        with client.session_transaction() as sess:
            user_id = sess.get('_user_id')
            assert user_id is not None
            assert int(user_id) == admin_user.id

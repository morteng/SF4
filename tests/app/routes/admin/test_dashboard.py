import pytest
from flask import url_for, generate_csrf

@pytest.mark.usefixtures('app', 'client', 'admin_user')
def test_dashboard_data(client, admin_user, app):
    # Push a request context to generate CSRF token and URL generation
    with app.test_request_context():
        csrf_token = generate_csrf()
        login_url = url_for('public.login')

    # Log in the admin user
    response = client.post(login_url, data={
        'username': admin_user.username,
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    # Add assertions to check if login was successful and dashboard is accessible
    assert response.status_code == 200
    # Add more assertions as needed to verify the dashboard data

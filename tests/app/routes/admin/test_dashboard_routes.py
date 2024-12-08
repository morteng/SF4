from flask import url_for
import pytest

@pytest.fixture(scope='function')
def admin_user(client, session):
    from app.models.user import User
    user = User(username='admin', email='admin@example.com', is_admin=True)
    user.set_password('password123')
    session.add(user)
    session.commit()
    return user

def test_dashboard_data(client, app, admin_user):
    with client:
        # Log in the admin user
        response = client.post(url_for('user.login'), data={
            'username': admin_user.username,
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Access the dashboard data endpoint
        response = client.get(url_for('admin.dashboard.data'))
        assert response.status_code == 200
        assert b'Stipend Count:' in response.data
        assert b'Recent Bot Logs:' in response.data

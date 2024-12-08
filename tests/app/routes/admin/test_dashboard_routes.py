from flask import url_for, g
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
    # Log in the admin user
    with client.session_transaction() as sess:
        csrf_token = sess.get_csrf_token()

    response = client.post(url_for('public.login'), data={
        'username': admin_user.username,
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200

    # Ensure the user is logged in by checking the session variable
    with client.session_transaction() as sess:
        print(f"Session after login: {sess}")  # Debugging statement
        assert 'user_id' in sess and sess['user_id'] == admin_user.id

    # Access the dashboard data endpoint
    response = client.get(url_for('admin.dashboard.data'))
    print(f"Response status code: {response.status_code}")  # Debugging statement
    print(f"Response data: {response.data}")  # Debugging statement
    assert response.status_code == 200
    assert b'Stipend Count:' in response.data
    assert b'Recent Bot Logs:' in response.data

    # Ensure current_user is set correctly
    with app.test_request_context():
        from flask_login import current_user
        print(f"Current user: {current_user}")  # Debugging statement
        assert current_user.is_authenticated
        assert current_user.id == admin_user.id

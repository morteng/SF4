import pytest
from flask import url_for
from app.models.user import User
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def test_user(db_session):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    yield user

    # Teardown: Attempt to delete the user and rollback if an error occurs
    try:
        db_session.delete(user)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test user during teardown: {e}")
        db_session.rollback()

def test_login_route(client, test_user):
    login_response = client.get(url_for('public.login'))
    assert login_response.status_code == 200

    csrf_token = extract_csrf_token(login_response.data)
    response = client.post(url_for('public.login'), data={
        'username': test_user.username,
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    with client.session_transaction() as session:
        assert '_user_id' in session

def test_logout_route(logged_in_client):
    logout_response = logged_in_client.get(url_for('public.logout'))
    assert logout_response.status_code == 302
    with logged_in_client.session_transaction() as session:
        assert '_user_id' not in session

def test_index_route(client):
    index_response = client.get(url_for('public.index'))
    assert index_response.status_code == 200

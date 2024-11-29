import re
import pytest

@pytest.mark.usefixtures("admin_user")
def test_create_bot_api(client, session):
    # Get the login page to retrieve the CSRF token
    response = client.get('/admin/auth/login')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    csrf_token = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', html).group(1)

    # Log in as admin with the CSRF token
    response = client.post('/admin/auth/login', data={
        'username': 'admin',
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data

    # Create a new bot via API
    response = client.post('/api/bots', json={
        'name': 'TestBot',
        'description': 'A test bot',
        'status': 'active'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['name'] == 'TestBot'
    assert data['description'] == 'A test bot'
    assert data['status'] == 'active'

    # Verify in database
    from app.models.bot import Bot
    bot = session.query(Bot).filter_by(name='TestBot').first()
    assert bot is not None

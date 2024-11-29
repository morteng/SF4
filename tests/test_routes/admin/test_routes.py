import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module', autouse=True)
def init_admin_user(db):
    # First try to find existing admin user
    from app.models.user import User  # Import the User model inside the fixture
    admin_user = db.session.query(User).filter_by(email='admin@example.com').first()
    if not admin_user:
        admin_user = User(
            username='admin_user',
            password_hash='pbkdf2:sha256:150000$XbL3IjWn$3d8Kq7J29e4gFyhiuQlZIl12tXcVU8S2R5Qx5hPZV0k=',
            email='admin@example.com',
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

def test_admin_login(client):
    response = client.post('/admin/login', json={
        'username': 'admin_user',
        'password': 'secure_password'
    })
    assert response.status_code == 200
    assert b'Admin login successful' in response.data

def test_create_stipend(client, session):
    response = client.post('/admin/stipends', json={
        'name': 'Sample Stipend',
        'summary': 'Sample summary',
        'description': 'Sample description',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Apply here',
        'eligibility_criteria': 'Eligible criteria',
        'application_deadline': '2023-12-31',
        'open_for_applications': True
    })
    assert response.status_code == 201
    assert b'Stipend created successfully' in response.data

def test_update_stipend(client, session):
    # Create a stipend first
    from app.models.stipend import Stipend
    stipend = Stipend(
        name='Sample Stipend',
        summary='Sample summary',
        description='Sample description',
        homepage_url='http://example.com',
        application_procedure='Apply here',
        eligibility_criteria='Eligible criteria',
        application_deadline='2023-12-31',
        open_for_applications=True
    )
    session.add(stipend)
    session.commit()

    response = client.put(f'/admin/stipends/{stipend.id}', json={
        'name': 'Updated Stipend',
        'summary': 'Updated summary'
    })
    assert response.status_code == 200
    assert b'Stipend updated successfully' in response.data

def test_delete_stipend(client, session):
    # Create a stipend first
    from app.models.stipend import Stipend
    stipend = Stipend(
        name='Sample Stipend',
        summary='Sample summary',
        description='Sample description',
        homepage_url='http://example.com',
        application_procedure='Apply here',
        eligibility_criteria='Eligible criteria',
        application_deadline='2023-12-31',
        open_for_applications=True
    )
    session.add(stipend)
    session.commit()

    response = client.delete(f'/admin/stipends/{stipend.id}')
    assert response.status_code == 200
    assert b'Stipend deleted successfully' in response.data

def test_create_tag(client, session):
    response = client.post('/admin/tags', json={
        'name': 'Sample Tag',
        'category': 'Category'
    })
    assert response.status_code == 201
    assert b'Tag created successfully' in response.data

def test_update_tag(client, session):
    # Create a tag first
    from app.models.tag import Tag
    tag = Tag(name='Sample Tag', category='Category')
    session.add(tag)
    session.commit()

    response = client.put(f'/admin/tags/{tag.id}', json={
        'name': 'Updated Tag',
        'category': 'Updated Category'
    })
    assert response.status_code == 200
    assert b'Tag updated successfully' in response.data

def test_delete_tag(client, session):
    # Create a tag first
    from app.models.tag import Tag
    tag = Tag(name='Sample Tag', category='Category')
    session.add(tag)
    session.commit()

    response = client.delete(f'/admin/tags/{tag.id}')
    assert response.status_code == 200
    assert b'Tag deleted successfully' in response.data

def test_create_organization(client, session):
    response = client.post('/admin/organizations', json={
        'name': 'Sample Organization',
        'description': 'Sample description',
        'homepage_url': 'http://example.com'
    })
    assert response.status_code == 201
    assert b'Organization created successfully' in response.data

def test_update_organization(client, session):
    # Create an organization first
    from app.models.organization import Organization
    organization = Organization(
        name='Sample Organization',
        description='Sample description',
        homepage_url='http://example.com'
    )
    session.add(organization)
    session.commit()

    response = client.put(f'/admin/organizations/{organization.id}', json={
        'name': 'Updated Organization',
        'description': 'Updated description'
    })
    assert response.status_code == 200
    assert b'Organization updated successfully' in response.data

def test_delete_organization(client, session):
    # Create an organization first
    from app.models.organization import Organization
    organization = Organization(
        name='Sample Organization',
        description='Sample description',
        homepage_url='http://example.com'
    )
    session.add(organization)
    session.commit()

    response = client.delete(f'/admin/organizations/{organization.id}')
    assert response.status_code == 200
    assert b'Organization deleted successfully' in response.data

def test_create_bot(client, session):
    response = client.post('/admin/bots', json={
        'name': 'Sample Bot',
        'description': 'Sample description',
        'status': 'active'
    })
    assert response.status_code == 201
    assert b'Bot created successfully' in response.data

def test_update_bot(client, session):
    # Create a bot first
    from app.models.bot import Bot
    bot = Bot(name='Sample Bot', description='Sample description', status='active')
    session.add(bot)
    session.commit()

    response = client.put(f'/admin/bots/{bot.id}', json={
        'name': 'Updated Bot',
        'description': 'Updated description',
        'status': 'inactive'
    })
    assert response.status_code == 200
    assert b'Bot updated successfully' in response.data

def test_delete_bot(client, session):
    # Create a bot first
    from app.models.bot import Bot
    bot = Bot(name='Sample Bot', description='Sample description', status='active')
    session.add(bot)
    session.commit()

    response = client.delete(f'/admin/bots/{bot.id}')
    assert response.status_code == 200
    assert b'Bot deleted successfully' in response.data

def test_create_notification(client, session):
    response = client.post('/admin/notifications', json={
        'message': 'Sample notification',
        'type': 'info'
    })
    assert response.status_code == 201
    assert b'Notification created successfully' in response.data

def test_update_notification(client, session):
    # Create a notification first
    from app.models.notification import Notification
    notification = Notification(message='Sample notification', type='info')
    session.add(notification)
    session.commit()

    response = client.put(f'/admin/notifications/{notification.id}', json={
        'message': 'Updated notification',
        'type': 'warning'
    })
    assert response.status_code == 200
    assert b'Notification updated successfully' in response.data

def test_delete_notification(client, session):
    # Create a notification first
    from app.models.notification import Notification
    notification = Notification(message='Sample notification', type='info')
    session.add(notification)
    session.commit()

    response = client.delete(f'/admin/notifications/{notification.id}')
    assert response.status_code == 200
    assert b'Notification deleted successfully' in response.data

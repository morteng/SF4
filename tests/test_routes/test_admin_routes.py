import pytest
from app import create_app, db
from app.models.user import User
from app.models.stipend import Stipend
from app.models.tag import Tag
from app.models.organization import Organization
from app.models.bot import Bot
from app.models.notification import Notification

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def init_database(test_client):
    db.create_all()
    admin_user = User(username='admin_user', password_hash='hashed_password', email='admin@example.com', is_admin=True)
    db.session.add(admin_user)
    db.session.commit()

def test_admin_login(test_client, init_database):
    response = test_client.post('/admin/login', json={
        'username': 'admin_user',
        'password': 'secure_password'
    })
    assert response.status_code == 200
    assert b'Admin login successful' in response.data

def test_create_stipend(test_client, init_database):
    response = test_client.post('/admin/stipends', json={
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

def test_update_stipend(test_client, init_database):
    # Create a stipend first
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
    db.session.add(stipend)
    db.session.commit()

    response = test_client.put(f'/admin/stipends/{stipend.id}', json={
        'name': 'Updated Stipend',
        'summary': 'Updated summary'
    })
    assert response.status_code == 200
    assert b'Stipend updated successfully' in response.data

def test_delete_stipend(test_client, init_database):
    # Create a stipend first
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
    db.session.add(stipend)
    db.session.commit()

    response = test_client.delete(f'/admin/stipends/{stipend.id}')
    assert response.status_code == 200
    assert b'Stipend deleted successfully' in response.data

def test_create_tag(test_client, init_database):
    response = test_client.post('/admin/tags', json={
        'name': 'Sample Tag',
        'category': 'Category'
    })
    assert response.status_code == 201
    assert b'Tag created successfully' in response.data

def test_update_tag(test_client, init_database):
    # Create a tag first
    tag = Tag(name='Sample Tag', category='Category')
    db.session.add(tag)
    db.session.commit()

    response = test_client.put(f'/admin/tags/{tag.id}', json={
        'name': 'Updated Tag',
        'category': 'Updated Category'
    })
    assert response.status_code == 200
    assert b'Tag updated successfully' in response.data

def test_delete_tag(test_client, init_database):
    # Create a tag first
    tag = Tag(name='Sample Tag', category='Category')
    db.session.add(tag)
    db.session.commit()

    response = test_client.delete(f'/admin/tags/{tag.id}')
    assert response.status_code == 200
    assert b'Tag deleted successfully' in response.data

def test_create_organization(test_client, init_database):
    response = test_client.post('/admin/organizations', json={
        'name': 'Sample Organization',
        'description': 'Sample description',
        'homepage_url': 'http://example.com'
    })
    assert response.status_code == 201
    assert b'Organization created successfully' in response.data

def test_update_organization(test_client, init_database):
    # Create an organization first
    organization = Organization(
        name='Sample Organization',
        description='Sample description',
        homepage_url='http://example.com'
    )
    db.session.add(organization)
    db.session.commit()

    response = test_client.put(f'/admin/organizations/{organization.id}', json={
        'name': 'Updated Organization',
        'description': 'Updated description'
    })
    assert response.status_code == 200
    assert b'Organization updated successfully' in response.data

def test_delete_organization(test_client, init_database):
    # Create an organization first
    organization = Organization(
        name='Sample Organization',
        description='Sample description',
        homepage_url='http://example.com'
    )
    db.session.add(organization)
    db.session.commit()

    response = test_client.delete(f'/admin/organizations/{organization.id}')
    assert response.status_code == 200
    assert b'Organization deleted successfully' in response.data

def test_create_bot(test_client, init_database):
    response = test_client.post('/admin/bots', json={
        'name': 'Sample Bot',
        'description': 'Sample description',
        'status': 'active'
    })
    assert response.status_code == 201
    assert b'Bot created successfully' in response.data

def test_update_bot(test_client, init_database):
    # Create a bot first
    bot = Bot(name='Sample Bot', description='Sample description', status='active')
    db.session.add(bot)
    db.session.commit()

    response = test_client.put(f'/admin/bots/{bot.id}', json={
        'name': 'Updated Bot',
        'description': 'Updated description',
        'status': 'inactive'
    })
    assert response.status_code == 200
    assert b'Bot updated successfully' in response.data

def test_delete_bot(test_client, init_database):
    # Create a bot first
    bot = Bot(name='Sample Bot', description='Sample description', status='active')
    db.session.add(bot)
    db.session.commit()

    response = test_client.delete(f'/admin/bots/{bot.id}')
    assert response.status_code == 200
    assert b'Bot deleted successfully' in response.data

def test_create_notification(test_client, init_database):
    response = test_client.post('/admin/notifications', json={
        'message': 'Sample notification',
        'type': 'info'
    })
    assert response.status_code == 201
    assert b'Notification created successfully' in response.data

def test_update_notification(test_client, init_database):
    # Create a notification first
    notification = Notification(message='Sample notification', type='info')
    db.session.add(notification)
    db.session.commit()

    response = test_client.put(f'/admin/notifications/{notification.id}', json={
        'message': 'Updated notification',
        'type': 'warning'
    })
    assert response.status_code == 200
    assert b'Notification updated successfully' in response.data

def test_delete_notification(test_client, init_database):
    # Create a notification first
    notification = Notification(message='Sample notification', type='info')
    db.session.add(notification)
    db.session.commit()

    response = test_client.delete(f'/admin/notifications/{notification.id}')
    assert response.status_code == 200
    assert b'Notification deleted successfully' in response.data

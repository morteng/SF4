import pytest
from bs4 import BeautifulSoup
from app.models.organization import Organization
from app.services.user_service import create_user

@pytest.fixture
def user(db_session):
    # Create a test user with admin privileges
    user = create_user({
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword',
        'is_admin': True  # Set is_admin to True
    })
    db_session.commit()
    return user

@pytest.fixture
def logged_in_client(client, user):
    # Log in the test user
    client.post('/login', data={
        'username': user.username,
        'password': 'testpassword'
    })
    return client

@pytest.mark.usefixtures("db_session")
class TestOrganizationRoutes:

    def test_list_organizations(self, logged_in_client, app):
        # Ensure no existing app context
        if hasattr(flask.g, 'app'):
            flask.g.pop('app', None)
        
        with app.app_context():
            response = logged_in_client.get('/admin/organizations/')
            assert response.status_code == 200
            soup = BeautifulSoup(response.data.decode(), 'html.parser')
            assert soup.find('h1', string='Manage Organizations')

    def test_create_organization(self, logged_in_client, app, db_session):
        # Ensure no existing app context
        if hasattr(flask.g, 'app'):
            flask.g.pop('app', None)
        
        with app.app_context():
            response = logged_in_client.post(
                '/admin/organizations/create',
                data={
                    'name': 'Test Org',
                    'description': 'A test organization for coverage',
                    'homepage_url': 'http://test.org'
                },
                follow_redirects=True
            )
            assert response.status_code == 200
            assert Organization.query.filter_by(name='Test Org').first() is not None

    def test_update_organization(self, logged_in_client, app, db_session):
        # Ensure no existing app context
        if hasattr(flask.g, 'app'):
            flask.g.pop('app', None)
        
        # Create an organization first
        with app.app_context():
            org = Organization(
                name='Old Name',
                description='Old Description',
                homepage_url='http://old.org'
            )
            db_session.add(org)
            db_session.commit()

            # Update the organization
            response = logged_in_client.put(
                f'/admin/organizations/{org.id}',
                json={
                    'name': 'Updated Name',
                    'description': 'Updated Description',
                    'homepage_url': 'http://updated.org'
                },
                follow_redirects=True
            )
            assert response.status_code == 200
            updated_org = Organization.query.get(org.id)
            assert updated_org.name == 'Updated Name'

    def test_delete_organization(self, logged_in_client, app, db_session):
        # Ensure no existing app context
        if hasattr(flask.g, 'app'):
            flask.g.pop('app', None)
        
        # Create an organization first
        with app.app_context():
            org = Organization(
                name='ToDelete',
                description='For deletion',
                homepage_url='http://delete.org'
            )
            db_session.add(org)
            db_session.commit()

            # Delete the organization
            response = logged_in_client.post(
                f'/admin/organizations/delete/{org.id}',
                follow_redirects=True
            )
            assert response.status_code == 200
            assert Organization.query.get(org.id) is None

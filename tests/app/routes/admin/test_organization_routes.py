import pytest
from bs4 import BeautifulSoup
from app.models.organization import Organization

@pytest.mark.usefixtures("db")
class TestOrganizationRoutes:

    def test_list_organizations(self, logged_in_client):
        # Test listing organizations
        response = logged_in_client.get('/organizations/')
        assert response.status_code == 200
        soup = BeautifulSoup(response.data.decode(), 'html.parser')
        assert soup.find('h1', string='List of Organizations')

    def test_create_organization(self, logged_in_client):
        # Test creating a new organization
        response = logged_in_client.post('/organizations/create', data={
            'name': 'Test Org',
            'description': 'A test organization for coverage',
            'homepage_url': 'http://test.org'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert Organization.query.filter_by(name='Test Org').first() is not None

    def test_update_organization(self, logged_in_client):
        # Create an organization first
        org = Organization(name='Old Name', description='Old Description', homepage_url='http://old.org')
        db.session.add(org)
        db.session.commit()

        # Update the organization
        response = logged_in_client.put(f'/organizations/{org.id}', json={
            'name': 'Updated Name',
            'description': 'Updated Description',
            'homepage_url': 'http://updated.org'
        }, follow_redirects=True)
        assert response.status_code == 200
        updated_org = Organization.query.get(org.id)
        assert updated_org.name == 'Updated Name'

    def test_delete_organization(self, logged_in_client):
        # Create an organization first
        org = Organization(name='ToDelete', description='For deletion', homepage_url='http://delete.org')
        db.session.add(org)
        db.session.commit()

        # Delete the organization
        response = logged_in_client.post(f'/organizations/delete/{org.id}', follow_redirects=True)
        assert response.status_code == 200
        assert Organization.query.get(org.id) is None

import logging
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest
from flask import url_for
from flask.testing import FlaskClient
from app.constants import FlashMessages
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.tag import Tag
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.extensions import db
from app.forms.admin_forms import StipendForm
from app.routes.admin.stipend_routes import register_stipend_routes

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@pytest.fixture(scope='module')
def test_app(app):
    register_stipend_routes(app)
    yield app

@pytest.fixture
def mock_form():
    form = MagicMock(spec=StipendForm)
    form.validate.return_value = True
    form.errors = {}
    return form

@pytest.fixture
def test_organization(db_session):
    org = Organization(name='Test Org')
    db_session.add(org)
    db_session.commit()
    return org

@pytest.fixture
def test_tags(db_session):
    tags = [Tag(name='Research', category='Academic'), Tag(name='Scholarship', category='Funding')]
    db_session.add_all(tags)
    db_session.commit()
    return tags

@pytest.fixture
def test_stipend(db_session, test_organization, test_tags):
    stipend = Stipend(
        name='Existing Stipend',
        summary='Existing summary',
        description='Existing description',
        homepage_url='http://existing.com',
        application_procedure='Existing procedure',
        eligibility_criteria='Existing criteria',
        application_deadline=datetime.now() + timedelta(days=30),
        open_for_applications=True,
        organization_id=test_organization.id
    )
    stipend.tags = test_tags
    db_session.add(stipend)
    db_session.commit()
    return stipend

def get_csrf_token(client: FlaskClient, endpoint: str, **kwargs) -> str:
    response = client.get(url_for(endpoint, **kwargs))
    assert response.status_code == 200, f"Failed to load {endpoint} page."
    return response.data.decode().split('csrf_token" value="')[1].split('"')[0]

class TestStipendRoutes:
    
    @pytest.mark.parametrize("invalid_data,expected_error", [
        ({'name': None}, b"Name is required"),
        ({'organization_id': None}, b"Organization is required"),
        ({'application_deadline': 'invalid-date'}, b"Invalid date format"),
        ({'tags': ['invalid']}, b"Invalid tag ID")
    ])
    def test_create_stipend_invalid_data(self, authenticated_admin, test_organization, test_tags, invalid_data, expected_error):
        csrf_token = get_csrf_token(authenticated_admin, 'admin.stipend.create')
        form_data = {
            'name': 'Test Stipend',
            'summary': 'Test summary',
            'description': 'Test description',
            'homepage_url': 'http://example.com',
            'application_procedure': 'Apply online',
            'eligibility_criteria': 'Open to all',
            'application_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'organization_id': str(test_organization.id),
            'tags': [str(tag.id) for tag in test_tags],
            'csrf_token': csrf_token
        }
        form_data.update(invalid_data)
        response = authenticated_admin.post(url_for('admin.stipend.create'), data=form_data, follow_redirects=True)
        assert response.status_code == 400
        assert expected_error in response.data

    def test_create_stipend_success(self, authenticated_admin, test_organization, test_tags):
        csrf_token = get_csrf_token(authenticated_admin, 'admin.stipend.create')
        form_data = {
            'name': 'Test Stipend',
            'summary': 'Test summary',
            'description': 'Test description',
            'homepage_url': 'http://example.com',
            'application_procedure': 'Apply online',
            'eligibility_criteria': 'Open to all',
            'application_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'organization_id': str(test_organization.id),
            'tags': [str(tag.id) for tag in test_tags],
            'csrf_token': csrf_token
        }
        response = authenticated_admin.post(url_for('admin.stipend.create'), data=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert FlashMessages.CREATE_SUCCESS.value.encode() in response.data
        stipend = Stipend.query.filter_by(name='Test Stipend').first()
        assert stipend is not None

    def test_update_stipend_success(self, authenticated_admin, test_stipend):
        csrf_token = get_csrf_token(authenticated_admin, 'admin.stipend.edit', id=test_stipend.id)
        updated_data = {
            'name': 'Updated Stipend',
            'summary': test_stipend.summary,
            'description': test_stipend.description,
            'homepage_url': test_stipend.homepage_url,
            'application_procedure': test_stipend.application_procedure,
            'eligibility_criteria': test_stipend.eligibility_criteria,
            'application_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
            'organization_id': str(test_stipend.organization_id),
            'tags': [str(tag.id) for tag in test_stipend.tags],
            'csrf_token': csrf_token
        }
        response = authenticated_admin.post(url_for('admin.stipend.edit', id=test_stipend.id), data=updated_data, follow_redirects=True)
        assert response.status_code == 200
        assert FlashMessages.UPDATE_SUCCESS.value.encode() in response.data
        stipend = Stipend.query.get(test_stipend.id)
        assert stipend.name == 'Updated Stipend'

    def test_delete_stipend_success(self, authenticated_admin, test_stipend):
        response = authenticated_admin.post(url_for('admin.stipend.delete', id=test_stipend.id), follow_redirects=True)
        assert response.status_code == 200
        assert FlashMessages.DELETE_SUCCESS.value.encode() in response.data
        stipend = Stipend.query.get(test_stipend.id)
        assert stipend is None

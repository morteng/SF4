import logging
from datetime import datetime, timedelta

import pytest
from flask import url_for
from flask.testing import FlaskClient
from pytz import timezone

from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.tag import Tag
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.constants import FlashMessages
from tests.conftest import extract_csrf_token
from tests.utils import AuthActions

logger = logging.getLogger(__name__)


@pytest.fixture
def authenticated_admin(client: FlaskClient, auth: AuthActions) -> FlaskClient:
    """Fixture to authenticate as an admin user."""
    auth.login()
    return client


@pytest.fixture(scope='function')
def stipend_data():
    """Provide default stipend data for testing."""
    return {
        'name': 'Test Stipend',
        'summary': 'This is a test stipend.',
        'description': 'Detailed description of the test stipend.',
        'homepage_url': 'http://example.com/stipend',
        'application_procedure': 'Apply online at example.com',
        'eligibility_criteria': 'Open to all students',
        'application_deadline': (
            datetime.now() + timedelta(days=365)
        ).strftime('%Y-%m-%d %H:%M:%S'),  # Future date
        'open_for_applications': True
    }


@pytest.fixture(scope='function')
def test_stipend(db_session, stipend_data):
    """Create and tear down a test stipend object."""
    # Convert string to datetime
    stipend_data['application_deadline'] = datetime.strptime(
        stipend_data['application_deadline'], '%Y-%m-%d %H:%M:%S'
    )
    organization = Organization(name='Test Org')
    db_session.add(organization)
    db_session.commit()

    stipend = Stipend(**stipend_data, organization_id=organization.id)
    db_session.add(stipend)
    db_session.commit()
    yield stipend

    db_session.delete(stipend)
    db_session.commit()


def get_csrf_token(client: FlaskClient, endpoint: str, **kwargs) -> str:
    """Helper to load a page, verify success, and extract CSRF token."""
    response = client.get(url_for(endpoint, **kwargs))
    assert response.status_code == 200, f"Failed to load {endpoint} page."
    return extract_csrf_token(response.data)


def create_test_stipend(authenticated_admin: FlaskClient, db_session) -> dict:
    """
    Helper function to create a test stipend and return form data with a valid CSRF token.
    This sets up an org, tags, and loads the create form.
    """
    organization = Organization(name='Test Org')
    tag1 = Tag(name='Research', category='Academic')
    tag2 = Tag(name='Scholarship', category='Funding')
    db_session.add_all([organization, tag1, tag2])
    db_session.commit()

    csrf_token = get_csrf_token(authenticated_admin, 'admin.stipend.create')

    return {
        'name': 'Test Stipend',
        'summary': 'Test summary',
        'description': 'Test description',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Apply online',
        'eligibility_criteria': 'Open to all',
        'application_deadline': (
            datetime.now(timezone.utc) + timedelta(days=30)
        ).strftime('%Y-%m-%d %H:%M:%S'),
        'organization_id': str(organization.id),
        'tags': [str(tag1.id), str(tag2.id)],
        'open_for_applications': True,
        'csrf_token': csrf_token
    }


def test_create_duplicate_stipend(authenticated_admin: FlaskClient, db_session) -> None:
    """Ensure that creating a stipend with the same name twice is not allowed."""
    # First create a valid stipend
    form_data = create_test_stipend(authenticated_admin, db_session)
    response = authenticated_admin.post(
        url_for('admin.stipend.create'),
        data=form_data,
        follow_redirects=True
    )
    assert response.status_code == 200

    # Attempt the same creation again
    csrf_token = get_csrf_token(authenticated_admin, 'admin.stipend.create')
    form_data['csrf_token'] = csrf_token

    response = authenticated_admin.post(
        url_for('admin.stipend.create'),
        data=form_data,
        follow_redirects=True
    )
    assert response.status_code == 400
    assert b'Stipend with this name already exists' in response.data


def test_create_stipend_with_invalid_references(authenticated_admin: FlaskClient, db_session) -> None:
    """Test validation for invalid organization and tag references."""
    csrf_token = get_csrf_token(authenticated_admin, 'admin.stipend.create')

    invalid_data = {
        'name': 'Invalid Ref Stipend',
        'summary': 'Test summary',
        'description': 'Test description',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Apply online',
        'eligibility_criteria': 'Open to all',
        'application_deadline': (
            datetime.now(timezone.utc) + timedelta(days=30)
        ).strftime('%Y-%m-%d %H:%M:%S'),
        'organization_id': '999',  # Invalid org ID
        'tags': ['999'],           # Invalid tag ID
        'open_for_applications': True,
        'csrf_token': csrf_token
    }

    response = authenticated_admin.post(
        url_for('admin.stipend.create'),
        data=invalid_data,
        follow_redirects=True
    )
    assert response.status_code == 400
    assert b'Invalid organization' in response.data
    assert b'Invalid tag' in response.data


def test_create_stipend_route(authenticated_admin: FlaskClient, db_session) -> None:
    """
    Test that a stipend can be created successfully through the admin interface,
    verifying audit log, notification, and success message.
    """
    # Create organization and tags
    organization = Organization(name='Test Org')
    tag1 = Tag(name='Research', category='Academic')
    tag2 = Tag(name='Scholarship', category='Funding')
    db_session.add_all([organization, tag1, tag2])
    db_session.commit()

    # Grab CSRF token
    csrf_token = get_csrf_token(authenticated_admin, 'admin.stipend.create')

    # Prepare form data
    form_data = {
        'name': 'Test Stipend',
        'summary': 'Test summary',
        'description': 'Test description',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Apply online',
        'eligibility_criteria': 'Open to all',
        'application_deadline': (
            datetime.now(timezone.utc) + timedelta(days=30)
        ).strftime('%Y-%m-%d %H:%M:%S'),
        'organization_id': str(organization.id),
        'tags': [str(tag1.id), str(tag2.id)],
        'open_for_applications': True,
        'csrf_token': csrf_token
    }

    # Submit form
    response = authenticated_admin.post(
        url_for('admin.stipend.create'),
        data=form_data,
        follow_redirects=True
    )
    assert response.status_code == 200

    # Check database
    created_stipend = Stipend.query.filter_by(name='Test Stipend').first()
    assert created_stipend is not None
    assert created_stipend.summary == 'Test summary'
    assert created_stipend.organization_id == organization.id
    assert len(created_stipend.tags) == 2

    # Verify logs and notifications
    audit_log = AuditLog.query.filter_by(object_type='Stipend', object_id=created_stipend.id).first()
    assert audit_log is not None
    assert audit_log.action == 'create_stipend'

    notification = Notification.query.filter_by(related_object=created_stipend).first()
    assert notification is not None
    assert notification.type == 'STIPEND_CREATED'

    assert FlashMessages.CREATE_STIPEND_SUCCESS.value.encode() in response.data


@pytest.mark.parametrize("invalid_date, expected_message", [
    ("2023-13-32 99:99:99", "Invalid date format"),
    ("2023-02-30 12:00:00", "Invalid date"),
    ("2023-04-31 12:00:00", "Invalid date"),
    ("2023-00-01 12:00:00", "Invalid date"),
    ("2023-01-00 12:00:00", "Invalid date"),
])
def test_create_stipend_with_invalid_dates(
    authenticated_admin: FlaskClient,
    stipend_data: dict,
    db_session,
    invalid_date: str,
    expected_message: str
) -> None:
    """Test validation of invalid application deadline dates."""
    logger.info(f"Starting test_create_stipend_with_invalid_dates: {invalid_date}")

    organization = Organization(name='Test Org Invalid Date')
    db_session.add(organization)
    db_session.commit()

    csrf_token = get_csrf_token(authenticated_admin, 'admin.stipend.create')

    invalid_data_payload = {
        'name': stipend_data['name'],
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': invalid_date,
        'organization_id': str(organization.id),
        'open_for_applications': True,
        'csrf_token': csrf_token
    }

    response = authenticated_admin.post(
        url_for('admin.stipend.create'),
        data=invalid_data_payload,
        follow_redirects=True
    )
    assert response.status_code == 400, "Expected 400 for invalid date"

    # Verify no stipend created
    stipends = Stipend.query.all()
    assert not any(s.name == invalid_data_payload['name'] for s in stipends), (
        "Stipend was incorrectly created"
    )

    # Check for the error message
    assert expected_message.encode() in response.data, (
        f"Expected error message for {invalid_date} not found"
    )
    logger.info(f"Completed test_create_stipend_with_invalid_dates: {invalid_date}")


def test_update_stipend_route(authenticated_admin: FlaskClient, test_stipend: Stipend, db_session) -> None:
    """Test stipend update via admin interface, including HTMX and non-HTMX handling."""
    logger.info("Starting test_update_stipend_route")

    update_response = authenticated_admin.get(url_for('admin.stipend.edit', id=test_stipend.id))
    assert update_response.status_code == 200, "Failed to load edit page"
    csrf_token = extract_csrf_token(update_response.data)

    updated_data = {
        'name': 'Updated Stipend',
        'summary': test_stipend.summary,
        'description': test_stipend.description,
        'homepage_url': test_stipend.homepage_url,
        'application_procedure': test_stipend.application_procedure,
        'eligibility_criteria': test_stipend.eligibility_criteria,
        'application_deadline': (
            datetime.now() + timedelta(days=365)
        ).strftime('%Y-%m-%d %H:%M:%S'),
        'organization_id': test_stipend.organization_id,
        'open_for_applications': True,
        'csrf_token': csrf_token
    }

    # HTMX update
    htmx_response = authenticated_admin.post(
        url_for('admin.stipend.edit', id=test_stipend.id),
        data=updated_data,
        headers={'HX-Request': 'true'}
    )
    assert htmx_response.status_code == 200, "HTMX update failed"
    assert b'<tr hx-target="this" hx-swap="outerHTML">' in htmx_response.data, (
        "HTMX response format incorrect"
    )

    # Non-HTMX update
    non_htmx_response = authenticated_admin.post(
        url_for('admin.stipend.edit', id=test_stipend.id),
        data=updated_data
    )
    assert non_htmx_response.status_code == 302, "Non-HTMX update failed"
    assert non_htmx_response.location.startswith('/admin/stipends/'), (
        "Incorrect redirect location"
    )

    final_response = authenticated_admin.get(non_htmx_response.location)
    assert final_response.status_code == 200, "Failed to load redirect page"

    updated_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert updated_stipend is not None, "Stipend not found"
    assert updated_stipend.name == 'Updated Stipend', "Name not updated"

    # Verify success message
    assert FlashMessages.UPDATE_STIPEND_SUCCESS.value.encode() in final_response.data


def test_delete_stipend_route(authenticated_admin: FlaskClient, test_stipend: Stipend, db_session) -> None:
    """Test stipend deletion via admin interface."""
    logger.info("Starting test_delete_stipend_route")

    response = authenticated_admin.post(
        url_for('admin.stipend.delete', id=test_stipend.id),
        follow_redirects=True
    )
    assert response.status_code == 200, "Failed to delete stipend"

    deleted_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert deleted_stipend is None, "Stipend was not deleted"
    assert FlashMessages.DELETE_STIPEND_SUCCESS.value.encode() in response.data


def test_index_stipend_route(authenticated_admin: FlaskClient, test_stipend: Stipend) -> None:
    """Test the stipend index page listing."""
    logger.info("Starting test_index_stipend_route")

    response = authenticated_admin.get(url_for('admin.admin_stipend.index'))
    assert response.status_code == 200, "Failed to load index page"
    assert test_stipend.name.encode() in response.data, "Stipend not listed in index"


def test_paginate_stipend_route(authenticated_admin: FlaskClient, test_stipend: Stipend) -> None:
    """Test stipend pagination route."""
    logger.info("Starting test_paginate_stipend_route")

    response = authenticated_admin.get(url_for('admin.stipend.paginate', page=1))
    assert response.status_code == 200, "Failed to load paginated page"
    assert test_stipend.name.encode() in response.data, "Stipend not in paginated results"


def test_create_stipend_route_htmx(logged_in_admin, stipend_data, db_session):
    """Test creating a stipend with HTMX headers."""
    organization = Organization(name='Test Org HTMX')
    db_session.add(organization)
    db_session.commit()
    stipend_data['organization_id'] = organization.id

    csrf_token = get_csrf_token(logged_in_admin, 'admin.stipend.create')

    response = logged_in_admin.post(
        url_for('admin.stipend.create'),
        headers={'HX-Request': 'true'},
        data={
            'name': stipend_data['name'],
            'summary': stipend_data['summary'],
            'description': stipend_data['description'],
            'homepage_url': stipend_data['homepage_url'],
            'application_procedure': stipend_data['application_procedure'],
            'eligibility_criteria': stipend_data['eligibility_criteria'],
            'application_deadline': stipend_data['application_deadline'],
            'organization_id': stipend_data['organization_id'],
            'open_for_applications': True,
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert (
        b'<tr id="stipend-row-' in response.data or
        b'Error rendering new row' in response.data
    ), "Row not rendered or no error feedback"

    created_stipend = Stipend.query.filter_by(name=stipend_data['name']).first()
    assert created_stipend is not None, "Stipend not created"
    assert created_stipend.summary == stipend_data['summary']
    assert FlashMessages.CREATE_STIPEND_SUCCESS.value.encode() in response.data


def test_create_stipend_route_with_invalid_application_deadline_format_htmx(
    logged_in_admin,
    stipend_data,
    db_session
):
    """Test stipend creation with an invalid date format (HTMX)."""
    organization = Organization(name='Test Org Invalid Deadline HTMX')
    db_session.add(organization)
    db_session.commit()

    csrf_token = get_csrf_token(logged_in_admin, 'admin.stipend.create')

    invalid_data = stipend_data.copy()
    invalid_data['application_deadline'] = '2023-13-32 99:99:99'

    response = logged_in_admin.post(
        url_for('admin.stipend.create'),
        headers={'HX-Request': 'true'},
        data={
            'name': invalid_data['name'],
            'summary': invalid_data['summary'],
            'description': invalid_data['description'],
            'homepage_url': invalid_data['homepage_url'],
            'application_procedure': invalid_data['application_procedure'],
            'eligibility_criteria': invalid_data['eligibility_criteria'],
            'application_deadline': invalid_data['application_deadline'],
            'organization_id': organization.id,
            'open_for_applications': invalid_data['open_for_applications'],
            'csrf_token': csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 400
    stipends = Stipend.query.all()
    assert not any(s.name == invalid_data['name'] for s in stipends), (
        "Stipend was created with invalid date"
    )
    assert b'Invalid date format. Please use YYYY-MM-DD HH:MM:SS' in response.data


def test_create_stipend_with_invalid_form_data_htmx(logged_in_admin, stipend_data, db_session):
    """Test HTMX form submission with invalid (empty) 'name' field."""
    organization = Organization(name='Test Org Invalid Form Data HTMX')
    db_session.add(organization)
    db_session.commit()

    csrf_token = get_csrf_token(logged_in_admin, 'admin.stipend.create')

    invalid_data = {
        'name': '',
        'summary': stipend_data['summary'],
        'description': stipend_data['description'],
        'homepage_url': stipend_data['homepage_url'],
        'application_procedure': stipend_data['application_procedure'],
        'eligibility_criteria': stipend_data['eligibility_criteria'],
        'application_deadline': stipend_data['application_deadline'],
        'organization_id': organization.id,
        'open_for_applications': stipend_data['open_for_applications'],
        'csrf_token': csrf_token
    }

    response = logged_in_admin.post(
        url_for('admin.stipend.create'),
        data=invalid_data,
        headers={'HX-Request': 'true'},
        follow_redirects=True
    )
    assert response.status_code == 400
    assert b'Name: Name is required.' in response.data, (
        "Expected 'Name is required' validation error"
    )

    # Ensure it wasn't created
    stipends = db_session.query(Stipend).all()
    assert not any(s.name == invalid_data['name'] for s in stipends)


def test_update_stipend_route_htmx(logged_in_admin, test_stipend, db_session):
    """Test updating a stipend with HTMX."""
    update_response = logged_in_admin.get(url_for('admin.stipend.edit', id=test_stipend.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': 'Updated Stipend',
        'summary': test_stipend.summary,
        'description': test_stipend.description,
        'homepage_url': test_stipend.homepage_url,
        'application_procedure': test_stipend.application_procedure,
        'eligibility_criteria': test_stipend.eligibility_criteria,
        'application_deadline': (
            datetime.now() + timedelta(days=1)
        ).strftime('%Y-%m-%d %H:%M:%S'),
        'organization_id': test_stipend.organization_id,
        'open_for_applications': test_stipend.open_for_applications,
        'csrf_token': csrf_token
    }

    response = logged_in_admin.post(
        url_for('admin.stipend.edit', id=test_stipend.id),
        headers={'HX-Request': 'true'},
        data=updated_data
    )
    assert response.status_code == 200

    updated_stipend = Stipend.query.filter_by(id=test_stipend.id).first()
    assert updated_stipend.name == 'Updated Stipend'
    assert FlashMessages.UPDATE_STIPEND_SUCCESS.value.encode() in response.data


# Example extra test snippet:
def test_create_stipend(client, admin_user, db):
    """
    A simpler example test:
    Logs in, creates a stipend, and checks the AuditLog for a 'create' action.
    """
    client.post('/login', data={'username': admin_user.username, 'password': 'password'})
    response = client.post('/admin/stipends/create', data={
        'name': 'Test Stipend',
        'summary': 'Test Summary',
        'description': 'Test Description',
        'homepage_url': 'https://example.com',
        'application_procedure': 'Test Procedure',
        'eligibility_criteria': 'Test Criteria',
        'application_deadline': '2025-12-31 23:59:59',
        'open_for_applications': True
    })
    assert response.status_code == 302

    stipend = Stipend.query.filter_by(name='Test Stipend').first()
    assert stipend is not None, "Stipend not created"

    audit_log = AuditLog.query.filter_by(object_type='stipend', object_id=stipend.id).first()
    assert audit_log is not None, "No audit log created"
    assert audit_log.action_type == 'create', "Audit log has incorrect action type"

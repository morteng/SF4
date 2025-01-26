import pytest
from datetime import datetime
from app.models.stipend import Stipend
from app.models.audit_log import AuditLog
from app.models.organization import Organization
from app.models.tag import Tag
from app.extensions import db

# Add freezegun availability check
try:
    from freezegun import freeze_time
    FREEZEGUN_INSTALLED = True
except ImportError:
    FREEZEGUN_INSTALLED = False

@pytest.fixture
def test_organization(db_session):
    """Create a test organization"""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    return org

@pytest.fixture
def test_tag(db_session):
    """Create a test tag"""
    tag = Tag(name="Test Tag")
    db_session.add(tag)
    db_session.commit()
    return tag

@pytest.mark.skipif(not FREEZEGUN_INSTALLED, reason="Requires freezegun")
def test_audit_log_creation(app, test_organization, test_tag):
    """Test audit log generation for stipend operations"""
    with app.app_context(), freeze_time("2024-01-01 12:00:00"):
        # Create initial stipend
        stipend_data = {
            'name': 'Test Stipend',
            'organization_id': test_organization.id,
            'tags': [test_tag.id]
        }
        
        # Create
        stipend = Stipend.create(stipend_data)
        create_log = AuditLog.query.filter_by(action='create_stipend').first()
        assert create_log.timestamp == datetime(2024, 1, 1, 12, 0)
        assert create_log.details_after['name'] == 'Test Stipend'

        # Update
        with freeze_time("2024-01-01 12:30:00"):
            stipend.update({'name': 'Updated Stipend'})
            update_log = AuditLog.query.filter_by(action='update_stipend').first()
            assert update_log.timestamp == datetime(2024, 1, 1, 12, 30)
            assert update_log.details_before['name'] == 'Test Stipend'
            assert update_log.details_after['name'] == 'Updated Stipend'

        # Delete
        with freeze_time("2024-01-01 13:00:00"):
            db.session.delete(stipend)
            db.session.commit()
            delete_log = AuditLog.query.filter_by(action='delete_stipend').first()
            assert delete_log.timestamp == datetime(2024, 1, 1, 13, 0)

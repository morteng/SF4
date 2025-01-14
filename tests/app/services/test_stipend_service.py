import pytest
import re
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, StaleDataError
from flask_login import login_user
from flask import get_flashed_messages
from app.models.tag import Tag
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.audit_log import AuditLog
from app.services.stipend_service import StipendService
from app.forms.admin_forms import StipendForm
from app.extensions import db
from app.constants import FlashMessages
import logging

# Configure logging
logger = logging.getLogger(__name__)

@pytest.fixture
def test_stipend_data():
    """Standard test data for stipend creation"""
    return {
        'name': 'Test Stipend',
        'summary': 'Test summary',
        'description': 'Test description',
        'homepage_url': 'http://example.com',
        'application_procedure': 'Apply online',
        'eligibility_criteria': 'Open to all',
        'application_deadline': (
            datetime.utcnow() + timedelta(days=30)
        ).strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True
    }

@pytest.fixture
def test_organization(db_session):
    """Create and return a test organization"""
    org = Organization(name='Test Org')
    db_session.add(org)
    db_session.commit()
    return org

@pytest.fixture
def test_tags(db_session):
    """Create and return test tags"""
    tags = [
        Tag(name='Research', category='Academic'),
        Tag(name='Scholarship', category='Funding')
    ]
    db_session.add_all(tags)
    db_session.commit()
    return tags

@pytest.fixture
def test_stipend(db_session, test_organization, test_tags):
    """Create and return a test stipend"""
    stipend = Stipend(
        name='Existing Stipend',
        summary='Existing summary',
        description='Existing description',
        homepage_url='http://existing.com',
        application_procedure='Existing procedure',
        eligibility_criteria='Existing criteria',
        application_deadline=datetime.utcnow() + timedelta(days=30),
        open_for_applications=True,
        organization_id=test_organization.id
    )
    stipend.tags = test_tags
    db_session.add(stipend)
    db_session.commit()
    return stipend

class TestStipendService:
    """Comprehensive test suite for StipendService"""

    # Test edge cases
    @pytest.mark.parametrize("invalid_data,expected_error", [
        # Missing required fields
        ({'name': None}, "Missing required field: name"),
        ({'organization_id': None}, "Missing required field: organization_id"),
        ({'application_deadline': None}, "Missing required field: application_deadline"),
    
        # Invalid field types
        ({'name': 123}, "Invalid name format"),
        ({'organization_id': 'abc'}, "Invalid organization ID"),
        ({'application_deadline': 123456}, "Invalid date format"),
    
        # Exceeding max lengths
        ({'name': 'A' * 101}, "Name exceeds maximum length"),
        ({'summary': 'B' * 501}, "Summary exceeds maximum length"),
        ({'description': 'C' * 2001}, "Description exceeds maximum length"),
    
        # Invalid URLs
        ({'homepage_url': 'invalid-url'}, "Invalid URL format"),
        ({'homepage_url': 'javascript:alert(1)'}, "Invalid URL scheme"),
    
        # Invalid boolean values
        ({'open_for_applications': 'maybe'}, "Invalid boolean value"),
    
        # Invalid tag IDs
        ({'tags': ['invalid']}, "Invalid tag ID format"),
        ({'tags': [99999]}, "Invalid tag ID"),
    
        # SQL injection attempts
        ({'name': "Test'; DROP TABLE stipends; --"}, "Invalid characters in name"),
    
        # XSS attempts
        ({'description': "<script>alert('XSS')</script>"}, "Invalid characters in description"),
    
        # Invalid unicode
        ({'name': b'\xff'.decode('latin1')}, "Invalid characters in name"),
    
        # Empty strings
        ({'name': '   '}, "Name cannot be empty"),
        ({'summary': '   '}, "Summary cannot be empty"),
    
        # Negative numbers
        ({'organization_id': -1}, "Invalid organization ID"),
    
        # Zero values
        ({'organization_id': 0}, "Invalid organization ID"),
    
        # String numbers
        ({'organization_id': '1'}, "Invalid organization ID format"),
    
        # Invalid date formats
        ({'application_deadline': '2023-02-30 12:00:00'}, "Invalid date format"),
        ({'application_deadline': '2023-04-31 12:00:00'}, "Invalid date format"),
        ({'application_deadline': '2023-00-01 12:00:00'}, "Invalid date format"),
        ({'application_deadline': '2023-01-00 12:00:00'}, "Invalid date format"),
        ({'application_deadline': 'invalid-date'}, "Invalid date format"),
        ({'application_deadline': ''}, "Invalid date format"),
        ({'application_deadline': None}, "Invalid date format")
    ])
    def test_create_stipend_invalid_data(self, test_data, test_organization, test_tags, invalid_data, expected_error):
        """Test stipend creation with various invalid data scenarios"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'organization_id': test_organization.id,
            'tags': [tag.id for tag in test_tags]
        })
        form_data.update(invalid_data)

        with pytest.raises(ValueError) as exc_info:
            service.create(form_data)
        
        assert expected_error in str(exc_info.value)

    # Test error conditions
    def test_create_stipend_database_error(self, test_data, test_organization, test_tags):
        """Test database error during stipend creation"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'organization_id': test_organization.id,
            'tags': [tag.id for tag in test_tags]
        })

        with patch('app.extensions.db.session.commit', side_effect=SQLAlchemyError("Database error")):
            with pytest.raises(SQLAlchemyError) as exc_info:
                service.create(form_data)
            assert "Database error" in str(exc_info.value)

    def test_create_stipend_audit_log_error(self, test_data, test_organization, test_tags):
        """Test audit logging error during stipend creation"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'organization_id': test_organization.id,
            'tags': [tag.id for tag in test_tags]
        })

        with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Audit log error")):
            with pytest.raises(Exception) as exc_info:
                service.create(form_data)
            assert "Audit log error" in str(exc_info.value)

    def test_create_stipend_rate_limit_exceeded(self, test_data, test_organization, test_tags):
        """Test rate limiting during stipend creation"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'organization_id': test_organization.id,
            'tags': [tag.id for tag in test_tags]
        })

        # Mock rate limiter to always fail
        with patch('app.services.base_service.BaseService._check_rate_limit', return_value=False):
            with pytest.raises(Exception) as exc_info:
                service.create(form_data)
            assert "Rate limit exceeded" in str(exc_info.value)

    # Test edge cases
    def test_create_stipend_with_max_length_fields(self, test_data, test_organization, test_tags):
        """Test creating stipend with maximum length fields"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'name': 'A' * 100,  # Max length
            'summary': 'B' * 500,
            'description': 'C' * 2000,
            'homepage_url': 'http://' + 'a' * 200 + '.com',
            'application_procedure': 'D' * 2000,
            'eligibility_criteria': 'E' * 2000,
            'organization_id': test_organization.id,
            'tags': [tag.id for tag in test_tags]
        })

        result = service.create(form_data)
        
        # Verify all fields were saved correctly
        stipend = Stipend.query.filter_by(name=form_data['name']).first()
        assert stipend is not None
        assert len(stipend.name) == 100
        assert len(stipend.summary) == 500
        assert len(stipend.description) == 2000

    def test_create_stipend_with_minimal_data(self, test_organization):
        """Test creating stipend with only required fields"""
        service = StipendService()
        minimal_data = {
            'name': 'Minimal Stipend',
            'organization_id': test_organization.id,
            'application_deadline': (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        }

        result = service.create(minimal_data)
        
        # Verify stipend was created with minimal data
        stipend = Stipend.query.filter_by(name='Minimal Stipend').first()
        assert stipend is not None
        assert stipend.summary is None
        assert stipend.description is None

    # Test update operations
    def test_update_stipend_with_empty_fields(self, test_stipend):
        """Test updating stipend with empty optional fields"""
        service = StipendService()
        update_data = {
            'name': 'Updated Stipend',
            'summary': '',
            'description': '',
            'organization_id': test_stipend.organization_id
        }

        result = service.update(test_stipend.id, update_data)
        
        # Verify update
        updated_stipend = Stipend.query.get(test_stipend.id)
        assert updated_stipend.name == 'Updated Stipend'
        assert updated_stipend.summary is None
        assert updated_stipend.description is None

    def test_update_stipend_with_invalid_data(self, test_stipend):
        """Test updating stipend with invalid data"""
        service = StipendService()
        invalid_data = {
            'name': '',  # Invalid name
            'application_deadline': 'invalid-date'
        }

        with pytest.raises(ValueError) as exc_info:
            service.update(test_stipend.id, invalid_data)
        
        errors = exc_info.value.args[0]
        assert 'name' in errors
        assert 'application_deadline' in errors

    # Test delete operations
    def test_delete_stipend_with_dependencies(self, test_stipend):
        """Test deleting stipend with dependent records"""
        service = StipendService()
        
        # Should still be able to delete
        result = service.delete(test_stipend.id)
        assert result is True
        
        # Verify deletion
        assert Stipend.query.get(test_stipend.id) is None
        assert Tag.query.count() == 2  # Tags should remain

    def test_delete_nonexistent_stipend(self):
        """Test deleting non-existent stipend"""
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.delete(9999)
        assert "Stipend not found" in str(exc_info.value)

    # Test relationship management
    def test_create_stipend_with_invalid_organization(self, test_data, test_tags):
        """Test creating stipend with invalid organization"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'organization_id': 99999,  # Invalid ID
            'tags': [tag.id for tag in test_tags]
        })

        with pytest.raises(ValueError) as exc_info:
            service.create(form_data)
        assert "Invalid organization" in str(exc_info.value)

    def test_create_stipend_with_invalid_tags(self, test_data, test_organization):
        """Test creating stipend with invalid tags"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'organization_id': test_organization.id,
            'tags': [99999]  # Invalid tag IDs
        })

        with pytest.raises(ValueError) as exc_info:
            service.create(form_data)
        assert "Invalid tags" in str(exc_info.value)

    # Test audit logging
    def test_audit_logging_on_create(self, test_data, test_organization, test_tags):
        """Test audit logging during stipend creation"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'organization_id': test_organization.id,
            'tags': [tag.id for tag in test_tags]
        })

        result = service.create(form_data)
        
        # Verify audit log was created
        log = AuditLog.query.filter_by(object_type='Stipend').first()
        assert log is not None
        assert log.action == 'create'
        assert log.object_id == result.id

    # Test rate limiting
    def test_rate_limiting_on_create(self, test_data, test_organization, test_tags):
        """Test rate limiting during stipend creation"""
        service = StipendService()
        form_data = test_data.copy()
        form_data.update({
            'organization_id': test_organization.id,
            'tags': [tag.id for tag in test_tags]
        })

        # Make 11 requests (default limit is 10 per minute)
        with pytest.raises(Exception) as exc_info:
            for _ in range(11):
                service.create(form_data)
        assert "Rate limit exceeded" in str(exc_info.value)

def test_database_constraint_violations(test_data, db_session, app, admin_user):
    """Test database constraint violations"""
    # Create initial valid stipend
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    valid_data = {
        'name': 'Valid Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test unique constraint violation
            service.create(valid_data)
            with pytest.raises(ValueError) as exc_info:
                service.create(valid_data)
            assert "already exists" in str(exc_info.value)
            
            # Test foreign key constraint violation
            invalid_data = {**valid_data, 'organization_id': 99999}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            assert "foreign key constraint" in str(exc_info.value).lower()

def test_htmx_partial_responses(test_data, db_session, app, admin_user):
    """Test HTMX partial response handling"""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    valid_data = {
        'name': 'HTMX Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test successful HTMX response
            result = service.create(valid_data, htmx_request=True)
            assert 'hx-redirect' in result.headers
            assert 'hx-trigger' in result.headers
            
            # Test HTMX error response
            invalid_data = {**valid_data, 'name': None}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data, htmx_request=True)
            assert 'hx-trigger' in exc_info.value.headers
            assert 'error' in exc_info.value.headers['hx-trigger']

def test_error_conditions(test_data, db_session, app, admin_user):
    """Test various error conditions"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test database connection failure
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "DB Error" in str(exc_info.value)
                
            # Test audit logging failure
            with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Log Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "Log Error" in str(exc_info.value)

def test_edge_cases(test_data, db_session, app, admin_user):
    """Test various edge cases"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test empty string handling
            empty_data = {
                'name': '   ',
                'organization_id': '',
                'application_deadline': ''
            }
            with pytest.raises(ValueError) as exc_info:
                service.create({**test_data, **empty_data})
            assert "cannot be empty" in str(exc_info.value)
            
            # Test maximum values
            max_data = {
                'name': 'A' * 100,
                'summary': 'B' * 500,
                'description': 'C' * 2000,
                'homepage_url': 'http://' + 'a' * 200 + '.com',
                'application_procedure': 'D' * 2000,
                'eligibility_criteria': 'E' * 2000
            }
            result = service.create({**test_data, **max_data})
            assert result is not None
            
            # Test minimum values
            min_data = {
                'name': 'A',
                'summary': 'B',
                'description': 'C',
                'homepage_url': 'http://a.com',
                'application_procedure': 'D',
                'eligibility_criteria': 'E'
            }
            result = service.create({**test_data, **min_data})
            assert result is not None

def test_database_constraint_violations(test_data, db_session, app, admin_user):
    """Test database constraint violations"""
    # Create initial valid stipend
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    valid_data = {
        'name': 'Valid Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test unique constraint violation
            service.create(valid_data)
            with pytest.raises(ValueError) as exc_info:
                service.create(valid_data)
            assert "already exists" in str(exc_info.value)
            
            # Test foreign key constraint violation
            invalid_data = {**valid_data, 'organization_id': 99999}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            assert "foreign key constraint" in str(exc_info.value).lower()

def test_htmx_partial_responses(test_data, db_session, app, admin_user):
    """Test HTMX partial response handling"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    valid_data = {
        'name': 'HTMX Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test successful HTMX response
            result = service.create(valid_data, htmx_request=True)
            assert 'hx-redirect' in result.headers
            assert 'hx-trigger' in result.headers
            
            # Test HTMX error response
            invalid_data = {**valid_data, 'name': None}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data, htmx_request=True)
            assert 'hx-trigger' in exc_info.value.headers
            assert 'error' in exc_info.value.headers['hx-trigger']

def test_error_conditions(test_data, db_session, app, admin_user):
    """Test various error conditions"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test database connection failure
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "DB Error" in str(exc_info.value)
                
            # Test audit logging failure
            with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Log Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "Log Error" in str(exc_info.value)

def test_edge_cases(test_data, db_session, app, admin_user):
    """Test various edge cases"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test empty string handling
            empty_data = {
                'name': '   ',
                'organization_id': '',
                'application_deadline': ''
            }
            with pytest.raises(ValueError) as exc_info:
                service.create({**test_data, **empty_data})
            assert "cannot be empty" in str(exc_info.value)
            
            # Test maximum values
            max_data = {
                'name': 'A' * 100,
                'summary': 'B' * 500,
                'description': 'C' * 2000,
                'homepage_url': 'http://' + 'a' * 200 + '.com',
                'application_procedure': 'D' * 2000,
                'eligibility_criteria': 'E' * 2000
            }
            result = service.create({**test_data, **max_data})
            assert result is not None
            
            # Test minimum values
            min_data = {
                'name': 'A',
                'summary': 'B',
                'description': 'C',
                'homepage_url': 'http://a.com',
                'application_procedure': 'D',
                'eligibility_criteria': 'E'
            }
            result = service.create({**test_data, **min_data})
            assert result is not None

def test_create_stipend_with_invalid_application_deadline_format(test_data, db_session, app, admin_user):
    # Test various invalid date formats
    invalid_formats = [
        '12/31/2023 23:59:59',  # Wrong format
        '2023-02-30 12:00:00',  # Invalid date
        '2023-13-01 12:00:00',  # Invalid month
        '2023-01-32 12:00:00',  # Invalid day
        '2023-01-01 25:00:00',  # Invalid hour
        '2023-01-01 12:60:00',  # Invalid minute
        '2023-01-01 12:00:60',  # Invalid second
        'invalid-date',         # Completely invalid
        '',                     # Empty string
        None                    # Null value
    ]
    
    for invalid_format in invalid_formats:
        test_data['application_deadline'] = invalid_format
        
        with app.app_context(), app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
            
            stipend_data = {k: v for k, v in test_data.items() if k != 'submit'}
            service = StipendService()
            
            with pytest.raises(ValueError) as exc_info:
                service.create(stipend_data)
            
            assert "Invalid date format" in str(exc_info.value)
            
            # Verify no record was created
            new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
            assert new_stipend is None

def test_create_stipend_with_invalid_unicode(test_data, db_session, app):
    """Test creating stipend with invalid unicode"""
    service = StipendService()
    
    invalid_unicode_cases = [
        {'name': b'\xff'.decode('latin1')},  # Invalid UTF-8
        {'summary': b'\xfe'.decode('latin1')},
        {'description': b'\xfd'.decode('latin1')}
    ]
    
    for case in invalid_unicode_cases:
        invalid_data = {**test_data, **case}
        with pytest.raises(ValueError):
            service.create(invalid_data)

def test_create_stipend_with_sql_injection_attempt(test_data, db_session, app):
    """Test creating stipend with SQL injection attempt"""
    service = StipendService()
    
    # Test SQL injection in name field
    test_data['name'] = "Test'; DROP TABLE stipends; --"
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Invalid characters" in str(exc_info.value)

def test_create_stipend_with_xss_attempt(test_data, db_session, app):
    """Test creating stipend with XSS attempt"""
    service = StipendService()
    
    # Test XSS in description field
    test_data['description'] = "<script>alert('XSS')</script>"
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Invalid characters" in str(exc_info.value)

def test_invalid_form_submissions(test_data, db_session, app, admin_user):
    """Test various invalid form submission scenarios"""
    invalid_cases = [
        # Missing required fields
        {'name': None, 'organization_id': None, 'application_deadline': None},
        # Invalid field types
        {'name': 123, 'organization_id': 'abc', 'application_deadline': 123456},
        # Exceeding max lengths
        {'name': 'A' * 101, 'summary': 'B' * 501, 'description': 'C' * 2001},
        # Invalid URLs
        {'homepage_url': 'invalid-url'},
        # Invalid boolean values
        {'open_for_applications': 'maybe'},
        # Invalid tag IDs
        {'tags': ['invalid']}
    ]

    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            for case in invalid_cases:
                invalid_data = {**test_data, **case}
                with pytest.raises(ValueError) as exc_info:
                    service.create(invalid_data)
                assert "validation error" in str(exc_info.value).lower()

def test_database_constraint_violations(test_data, db_session, app, admin_user):
    """Test database constraint violations"""
    # Create initial valid stipend
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    valid_data = {
        'name': 'Valid Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test unique constraint violation
            service.create(valid_data)
            with pytest.raises(ValueError) as exc_info:
                service.create(valid_data)
            assert "already exists" in str(exc_info.value)
            
            # Test foreign key constraint violation
            invalid_data = {**valid_data, 'organization_id': 99999}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            assert "foreign key constraint" in str(exc_info.value).lower()

def test_htmx_partial_responses(test_data, db_session, app, admin_user):
    """Test HTMX partial response handling"""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    valid_data = {
        'name': 'HTMX Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test successful HTMX response
            result = service.create(valid_data, htmx_request=True)
            assert 'hx-redirect' in result.headers
            assert 'hx-trigger' in result.headers
            
            # Test HTMX error response
            invalid_data = {**valid_data, 'name': None}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data, htmx_request=True)
            assert 'hx-trigger' in exc_info.value.headers
            assert 'error' in exc_info.value.headers['hx-trigger']

def test_error_conditions(test_data, db_session, app, admin_user):
    """Test various error conditions"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test database connection failure
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "DB Error" in str(exc_info.value)
                
            # Test audit logging failure
            with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Log Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "Log Error" in str(exc_info.value)

def test_edge_cases(test_data, db_session, app, admin_user):
    """Test various edge cases"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test empty string handling
            empty_data = {
                'name': '   ',
                'organization_id': '',
                'application_deadline': ''
            }
            with pytest.raises(ValueError) as exc_info:
                service.create({**test_data, **empty_data})
            assert "cannot be empty" in str(exc_info.value)
            
            # Test maximum values
            max_data = {
                'name': 'A' * 100,
                'summary': 'B' * 500,
                'description': 'C' * 2000,
                'homepage_url': 'http://' + 'a' * 200 + '.com',
                'application_procedure': 'D' * 2000,
                'eligibility_criteria': 'E' * 2000
            }
            result = service.create({**test_data, **max_data})
            assert result is not None
            
            # Test minimum values
            min_data = {
                'name': 'A',
                'summary': 'B',
                'description': 'C',
                'homepage_url': 'http://a.com',
                'application_procedure': 'D',
                'eligibility_criteria': 'E'
            }
            result = service.create({**test_data, **min_data})
            assert result is not None

def test_create_stipend_with_missing_required_fields(test_data, db_session, app, admin_user):
    """Test creation with missing required fields"""
    required_fields = ['name', 'organization_id', 'application_deadline']
    
    for field in required_fields:
        invalid_data = test_data.copy()
        invalid_data.pop(field)
        
        with app.app_context(), app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
            
            service = StipendService()
            
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            
            assert f"Missing required field: {field}" in str(exc_info.value)
            
            # Verify no record was created
            new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
            assert new_stipend is None

def test_create_stipend_with_invalid_organization(test_data, db_session, app, admin_user):
    """Test creation with invalid organization ID"""
    invalid_data = test_data.copy()
    invalid_data['organization_id'] = 99999  # Non-existent organization
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Invalid organization" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_invalid_tags(test_data, db_session, app, admin_user):
    """Test creation with invalid tag IDs"""
    invalid_data = test_data.copy()
    invalid_data['tags'] = [99999]  # Non-existent tag
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Invalid tags" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_past_deadline(test_data, db_session, app, admin_user):
    """Test creation with past deadline"""
    invalid_data = test_data.copy()
    invalid_data['application_deadline'] = '2020-01-01 00:00:00'  # Past date
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Deadline must be in the future" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_oversized_data(test_data, db_session, app):
    """Test creating stipend with oversized data"""
    service = StipendService()
    
    oversized_data = {
        'name': 'A' * 101,  # Exceeds max length
        'summary': 'B' * 501,
        'description': 'C' * 2001,
        'homepage_url': 'http://' + 'a' * 200 + '.com',
        'application_procedure': 'D' * 2001,
        'eligibility_criteria': 'E' * 2001
    }
    
    with pytest.raises(ValueError) as exc_info:
        service.create({**test_data, **oversized_data})
    assert "exceeds maximum length" in str(exc_info.value)

def test_create_stipend_with_invalid_boolean_values(test_data, db_session, app):
    """Test creating stipend with invalid boolean values"""
    service = StipendService()
    
    invalid_cases = [
        'maybe', 'yes', 'no', '1', '0', 'true', 'false', 'on', 'off'
    ]
    
    for case in invalid_cases:
        test_data['open_for_applications'] = case
        with pytest.raises(ValueError):
            service.create(test_data)

def test_create_stipend_with_invalid_url(test_data, db_session, app):
    """Test creating stipend with invalid URL"""
    service = StipendService()
    
    invalid_urls = [
        'invalid-url',
        'ftp://example.com',
        'javascript:alert(1)',
        'data:text/html,<script>alert(1)</script>'
    ]
    
    for url in invalid_urls:
        test_data['homepage_url'] = url
        with pytest.raises(ValueError):
            service.create(test_data)

def test_create_stipend_with_invalid_tag_ids(test_data, db_session, app):
    """Test creating stipend with invalid tag IDs"""
    service = StipendService()
    
    invalid_cases = [
        ['invalid'],  # Non-integer
        [99999],  # Non-existent
        [-1],  # Negative
        [0],  # Zero
        ['1', '2', '3']  # String numbers
    ]
    
    for case in invalid_cases:
        test_data['tags'] = case
        with pytest.raises(ValueError):
            service.create(test_data)

def test_create_stipend_with_duplicate_tags(test_data, db_session, app):
    """Test creating stipend with duplicate tags"""
    service = StipendService()
    
    # Create test tags
    tag1 = Tag(name='Test Tag 1')
    tag2 = Tag(name='Test Tag 2')
    db_session.add_all([tag1, tag2])
    db_session.commit()
    
    test_data['tags'] = [tag1.id, tag1.id]  # Duplicate tag IDs
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Duplicate tags" in str(exc_info.value)

def test_create_stipend_with_invalid_organization_relationship(test_data, db_session, app):
    """Test creating stipend with invalid organization relationship"""
    service = StipendService()
    
    # Create organization but delete it
    org = Organization(name='Test Org')
    db_session.add(org)
    db_session.commit()
    org_id = org.id
    db_session.delete(org)
    db_session.commit()
    
    test_data['organization_id'] = org_id
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Invalid organization" in str(exc_info.value)

def test_create_stipend_with_invalid_audit_logging(test_data, db_session, app):
    """Test creating stipend with audit logging failure"""
    service = StipendService()
    
    with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Audit log error")):
        with pytest.raises(Exception) as exc_info:
            service.create(test_data)
        assert "Audit log error" in str(exc_info.value)

def test_create_stipend_with_database_error(test_data, db_session, app):
    """Test creating stipend with database error"""
    service = StipendService()
    
    with patch('app.extensions.db.session.commit', side_effect=Exception("Database error")):
        with pytest.raises(Exception) as exc_info:
            service.create(test_data)
        assert "Database error" in str(exc_info.value)

def test_create_stipend_with_rate_limit_exceeded(test_data, db_session, app):
    """Test creating stipend with rate limit exceeded"""
    service = StipendService()
    
    # Create organization first
    org = Organization(name='Test Org')
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id
    
    # Make 11 requests (limit is 10 per minute)
    with pytest.raises(Exception) as exc_info:
        for _ in range(11):
            service.create(test_data)
    assert "Rate limit exceeded" in str(exc_info.value)

def test_invalid_form_submissions(test_data, db_session, app, admin_user):
    """Test various invalid form submission scenarios"""
    invalid_cases = [
        # Missing required fields
        {'name': None, 'organization_id': None, 'application_deadline': None},
        # Invalid field types
        {'name': 123, 'organization_id': 'abc', 'application_deadline': 123456},
        # Exceeding max lengths
        {'name': 'A' * 101, 'summary': 'B' * 501, 'description': 'C' * 2001},
        # Invalid URLs
        {'homepage_url': 'invalid-url'},
        # Invalid boolean values
        {'open_for_applications': 'maybe'},
        # Invalid tag IDs
        {'tags': ['invalid']}
    ]

    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            for case in invalid_cases:
                invalid_data = {**test_data, **case}
                with pytest.raises(ValueError) as exc_info:
                    service.create(invalid_data)
                assert "validation error" in str(exc_info.value).lower()

def test_database_constraint_violations(test_data, db_session, app, admin_user):
    """Test database constraint violations"""
    # Create initial valid stipend
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    valid_data = {
        'name': 'Valid Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test unique constraint violation
            service.create(valid_data)
            with pytest.raises(ValueError) as exc_info:
                service.create(valid_data)
            assert "already exists" in str(exc_info.value)
            
            # Test foreign key constraint violation
            invalid_data = {**valid_data, 'organization_id': 99999}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            assert "foreign key constraint" in str(exc_info.value).lower()

def test_htmx_partial_responses(test_data, db_session, app, admin_user):
    """Test HTMX partial response handling"""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    valid_data = {
        'name': 'HTMX Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test successful HTMX response
            result = service.create(valid_data, htmx_request=True)
            assert 'hx-redirect' in result.headers
            assert 'hx-trigger' in result.headers
            
            # Test HTMX error response
            invalid_data = {**valid_data, 'name': None}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data, htmx_request=True)
            assert 'hx-trigger' in exc_info.value.headers
            assert 'error' in exc_info.value.headers['hx-trigger']

def test_error_conditions(test_data, db_session, app, admin_user):
    """Test various error conditions"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test database connection failure
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "DB Error" in str(exc_info.value)
                
            # Test audit logging failure
            with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Log Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "Log Error" in str(exc_info.value)

def test_edge_cases(test_data, db_session, app, admin_user):
    """Test various edge cases"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test empty string handling
            empty_data = {
                'name': '   ',
                'organization_id': '',
                'application_deadline': ''
            }
            with pytest.raises(ValueError) as exc_info:
                service.create({**test_data, **empty_data})
            assert "cannot be empty" in str(exc_info.value)
            
            # Test maximum values
            max_data = {
                'name': 'A' * 100,
                'summary': 'B' * 500,
                'description': 'C' * 2000,
                'homepage_url': 'http://' + 'a' * 200 + '.com',
                'application_procedure': 'D' * 2000,
                'eligibility_criteria': 'E' * 2000
            }
            result = service.create({**test_data, **max_data})
            assert result is not None
            
            # Test minimum values
            min_data = {
                'name': 'A',
                'summary': 'B',
                'description': 'C',
                'homepage_url': 'http://a.com',
                'application_procedure': 'D',
                'eligibility_criteria': 'E'
            }
            result = service.create({**test_data, **min_data})
            assert result is not None

def test_create_stipend_with_missing_required_fields(test_data, db_session, app, admin_user):
    """Test creation with missing required fields"""
    required_fields = ['name', 'organization_id', 'application_deadline']
    
    for field in required_fields:
        invalid_data = test_data.copy()
        invalid_data.pop(field)
        
        with app.app_context(), app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
            
            service = StipendService()
            
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            
            assert f"Missing required field: {field}" in str(exc_info.value)
            
            # Verify no record was created
            new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
            assert new_stipend is None

def test_create_stipend_with_invalid_organization(test_data, db_session, app, admin_user):
    """Test creation with invalid organization ID"""
    invalid_data = test_data.copy()
    invalid_data['organization_id'] = 99999  # Non-existent organization
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Invalid organization" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_invalid_tags(test_data, db_session, app, admin_user):
    """Test creation with invalid tag IDs"""
    invalid_data = test_data.copy()
    invalid_data['tags'] = [99999]  # Non-existent tag
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Invalid tags" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_past_deadline(test_data, db_session, app, admin_user):
    """Test creation with past deadline"""
    invalid_data = test_data.copy()
    invalid_data['application_deadline'] = '2020-01-01 00:00:00'  # Past date
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        
        assert "Deadline must be in the future" in str(exc_info.value)
        
        # Verify no record was created
        new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
        assert new_stipend is None

def test_create_stipend_with_max_length_fields(test_data, db_session, app, admin_user):
    """Test creation with maximum length fields"""
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    # Set max length values
    test_data.update({
        'name': 'A' * 100,  # Max length
        'summary': 'B' * 500,
        'description': 'C' * 2000,
        'homepage_url': 'http://' + 'a' * 200 + '.com',
        'application_procedure': 'D' * 2000,
        'eligibility_criteria': 'E' * 2000,
        'organization_id': org.id
    })

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(test_data)
        
        # Verify all fields were saved correctly
        stipend = Stipend.query.filter_by(name=test_data['name']).first()
        assert stipend is not None
        assert len(stipend.name) == 100
        assert len(stipend.summary) == 500
        assert len(stipend.description) == 2000

def test_create_stipend_with_minimal_data(db_session, app, admin_user):
    """Test creation with only required fields"""
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    minimal_data = {
        'name': 'Minimal Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(minimal_data)
        
        # Verify stipend was created with minimal data
        stipend = Stipend.query.filter_by(name='Minimal Stipend').first()
        assert stipend is not None
        assert stipend.summary is None
        assert stipend.description is None

def test_update_stipend_with_empty_fields(test_data, db_session, app, admin_user):
    """Test updating with empty optional fields"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    update_data = {
        'name': 'Updated Stipend',
        'summary': '',
        'description': '',
        'organization_id': stipend.organization_id
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.update(stipend.id, update_data)
        
        # Verify update
        updated_stipend = Stipend.query.get(stipend.id)
        assert updated_stipend.name == 'Updated Stipend'
        assert updated_stipend.summary is None
        assert updated_stipend.description is None

def test_stipend_service_rate_limiting(test_data, app):
    """Test rate limiting in stipend service"""
    service = StipendService()
    
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Make 11 requests (limit is 10 per minute)
    with pytest.raises(Exception) as exc_info:
        for i in range(11):
            service.create(test_data)
            
    assert "Rate limit exceeded" in str(exc_info.value)

def test_stipend_service_audit_logging(test_data, db_session, app, admin_user):
    """Test audit logging in stipend service"""
    from app.models.audit_log import AuditLog
    
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(test_data)
        
        # Verify audit log was created
        log = AuditLog.query.filter_by(object_type='Stipend').first()
        assert log is not None
        assert log.action == 'create'
        assert log.object_id == result.id

def test_create_stipend_with_invalid_organization(test_data, db_session, app):
    """Test creating stipend with invalid organization"""
    test_data['organization_id'] = 9999  # Non-existent organization
    
    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "Invalid organization" in str(exc_info.value)

def test_create_stipend_with_deleted_organization(test_data, db_session, app):
    """Test creating stipend with deleted organization"""
    # Create then delete organization
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    org_id = org.id
    db_session.delete(org)
    db_session.commit()
    
    test_data['organization_id'] = org_id
    
    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "Invalid organization" in str(exc_info.value)

def test_create_stipend_with_invalid_tag_relationships(test_data, db_session, app):
    """Test creating stipend with invalid tag relationships"""
    # Create valid organization
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id
    
    # Test various invalid tag scenarios
    invalid_cases = [
        [99999],  # Non-existent tag
        [-1],     # Negative tag ID
        [0],      # Zero tag ID
        ['invalid'],  # String instead of int
        [1, 1]    # Duplicate tags
    ]
    
    service = StipendService()
    
    for case in invalid_cases:
        test_data['tags'] = case
        with pytest.raises(ValueError) as exc_info:
            service.create(test_data)
        assert "Invalid tags" in str(exc_info.value)

def test_create_stipend_with_database_errors(test_data, db_session, app):
    """Test creating stipend with database errors"""
    # Create valid organization
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id
    
    service = StipendService()
    
    # Test various database error scenarios
    with patch('app.extensions.db.session.commit', side_effect=SQLAlchemyError("Database error")):
        with pytest.raises(SQLAlchemyError) as exc_info:
            service.create(test_data)
        assert "Database error" in str(exc_info.value)
        
    with patch('app.extensions.db.session.flush', side_effect=IntegrityError(None, None, None)):
        with pytest.raises(IntegrityError):
            service.create(test_data)

def test_create_stipend_with_rate_limiting(test_data, db_session, app):
    """Test rate limiting during stipend creation"""
    # Create valid organization
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id
    
    service = StipendService()
    
    # Make 11 requests (limit is 10 per minute)
    with pytest.raises(Exception) as exc_info:
        for _ in range(11):
            service.create(test_data)
    assert "Rate limit exceeded" in str(exc_info.value)

def test_create_stipend_with_audit_log_failure(test_data, db_session, app):
    """Test audit logging failure during stipend creation"""
    # Create valid organization
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id
    
    service = StipendService()
    
    with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Audit log error")):
        with pytest.raises(Exception) as exc_info:
            service.create(test_data)
        assert "Audit log error" in str(exc_info.value)

def test_create_stipend_with_concurrent_modification(test_data, db_session, app):
    """Test concurrent modification scenarios"""
    # Create valid organization
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id
    
    service = StipendService()
    
    # Simulate concurrent modification
    with patch('app.extensions.db.session.commit', side_effect=StaleDataError()):
        with pytest.raises(StaleDataError):
            service.create(test_data)

def test_create_stipend_with_invalid_unicode(test_data, db_session, app):
    """Test creating stipend with invalid unicode"""
    service = StipendService()
    
    invalid_unicode_cases = [
        {'name': b'\xff'.decode('latin1')},  # Invalid UTF-8
        {'summary': b'\xfe'.decode('latin1')},
        {'description': b'\xfd'.decode('latin1')}
    ]
    
    for case in invalid_unicode_cases:
        invalid_data = {**test_data, **case}
        with pytest.raises(ValueError):
            service.create(invalid_data)

def test_create_stipend_with_sql_injection_attempt(test_data, db_session, app):
    """Test creating stipend with SQL injection attempt"""
    service = StipendService()
    
    # Test SQL injection in name field
    test_data['name'] = "Test'; DROP TABLE stipends; --"
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Invalid characters" in str(exc_info.value)

def test_create_stipend_with_xss_attempt(test_data, db_session, app):
    """Test creating stipend with XSS attempt"""
    service = StipendService()
    
    # Test XSS in description field
    test_data['description'] = "<script>alert('XSS')</script>"
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Invalid characters" in str(exc_info.value)

def test_create_stipend_with_malformed_data(test_data, db_session, app):
    """Test creating stipend with malformed data"""
    service = StipendService()
    
    # Test with non-dict input
    with pytest.raises(TypeError):
        service.create("invalid data")
        
    # Test with empty dict
    with pytest.raises(ValueError):
        service.create({})

def test_create_stipend_with_invalid_field_types(test_data, db_session, app):
    """Test creating stipend with invalid field types"""
    service = StipendService()
    
    invalid_cases = [
        {'name': 123},  # Invalid name type
        {'summary': 456},  # Invalid summary type
        {'description': 789},  # Invalid description type
        {'homepage_url': 123},  # Invalid URL type
        {'application_procedure': 456},  # Invalid procedure type
        {'eligibility_criteria': 789},  # Invalid criteria type
        {'application_deadline': 'invalid-date'},  # Invalid date format
        {'open_for_applications': 'maybe'},  # Invalid boolean
        {'organization_id': 'not-an-int'},  # Invalid organization ID type
        {'tags': 'not-a-list'}  # Invalid tags type
    ]
    
    for case in invalid_cases:
        invalid_data = {**test_data, **case}
        with pytest.raises(ValueError):
            service.create(invalid_data)

def test_create_stipend_with_sql_injection_attempt(test_data, db_session, app):
    """Test creating stipend with SQL injection attempt"""
    service = StipendService()
    
    # Test SQL injection in name field
    test_data['name'] = "Test'; DROP TABLE stipends; --"
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Invalid characters" in str(exc_info.value)

def test_create_stipend_with_xss_attempt(test_data, db_session, app):
    """Test creating stipend with XSS attempt"""
    service = StipendService()
    
    # Test XSS in description field
    test_data['description'] = "<script>alert('XSS')</script>"
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Invalid characters" in str(exc_info.value)

def test_create_stipend_with_oversized_data(test_data, db_session, app):
    """Test creating stipend with oversized data"""
    service = StipendService()
    
    oversized_data = {
        'name': 'A' * 101,  # Exceeds max length
        'summary': 'B' * 501,
        'description': 'C' * 2001,
        'homepage_url': 'http://' + 'a' * 200 + '.com',
        'application_procedure': 'D' * 2001,
        'eligibility_criteria': 'E' * 2001
    }
    
    with pytest.raises(ValueError) as exc_info:
        service.create({**test_data, **oversized_data})
    assert "exceeds maximum length" in str(exc_info.value)

def test_create_stipend_with_invalid_unicode(test_data, db_session, app):
    """Test creating stipend with invalid unicode"""
    service = StipendService()
    
    invalid_unicode_cases = [
        {'name': b'\xff'.decode('latin1')},  # Invalid UTF-8
        {'summary': b'\xfe'.decode('latin1')},
        {'description': b'\xfd'.decode('latin1')}
    ]
    
    for case in invalid_unicode_cases:
        invalid_data = {**test_data, **case}
        with pytest.raises(ValueError):
            service.create(invalid_data)

def test_create_stipend_with_missing_required_fields(test_data, db_session, app):
    """Test creating stipend with missing required fields"""
    service = StipendService()
    
    required_fields = ['name', 'organization_id', 'application_deadline']
    
    for field in required_fields:
        invalid_data = test_data.copy()
        invalid_data.pop(field)
        
        with pytest.raises(ValueError) as exc_info:
            service.create(invalid_data)
        assert f"Missing required field: {field}" in str(exc_info.value)

def test_create_stipend_with_invalid_boolean_values(test_data, db_session, app):
    """Test creating stipend with invalid boolean values"""
    service = StipendService()
    
    invalid_cases = [
        'maybe', 'yes', 'no', '1', '0', 'true', 'false', 'on', 'off'
    ]
    
    for case in invalid_cases:
        test_data['open_for_applications'] = case
        with pytest.raises(ValueError):
            service.create(test_data)

def test_create_stipend_with_invalid_url(test_data, db_session, app):
    """Test creating stipend with invalid URL"""
    service = StipendService()
    
    invalid_urls = [
        'invalid-url',
        'ftp://example.com',
        'javascript:alert(1)',
        'data:text/html,<script>alert(1)</script>'
    ]
    
    for url in invalid_urls:
        test_data['homepage_url'] = url
        with pytest.raises(ValueError):
            service.create(test_data)

def test_create_stipend_with_invalid_tag_ids(test_data, db_session, app):
    """Test creating stipend with invalid tag IDs"""
    service = StipendService()
    
    invalid_cases = [
        ['invalid'],  # Non-integer
        [99999],  # Non-existent
        [-1],  # Negative
        [0],  # Zero
        ['1', '2', '3']  # String numbers
    ]
    
    for case in invalid_cases:
        test_data['tags'] = case
        with pytest.raises(ValueError):
            service.create(test_data)

def test_create_stipend_with_duplicate_tags(test_data, db_session, app):
    """Test creating stipend with duplicate tags"""
    service = StipendService()
    
    # Create test tags
    tag1 = Tag(name='Test Tag 1')
    tag2 = Tag(name='Test Tag 2')
    db_session.add_all([tag1, tag2])
    db_session.commit()
    
    test_data['tags'] = [tag1.id, tag1.id]  # Duplicate tag IDs
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Duplicate tags" in str(exc_info.value)

def test_create_stipend_with_invalid_organization_relationship(test_data, db_session, app):
    """Test creating stipend with invalid organization relationship"""
    service = StipendService()
    
    # Create organization but delete it
    org = Organization(name='Test Org')
    db_session.add(org)
    db_session.commit()
    org_id = org.id
    db_session.delete(org)
    db_session.commit()
    
    test_data['organization_id'] = org_id
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
    assert "Invalid organization" in str(exc_info.value)

def test_create_stipend_with_invalid_audit_logging(test_data, db_session, app):
    """Test creating stipend with audit logging failure"""
    service = StipendService()
    
    with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Audit log error")):
        with pytest.raises(Exception) as exc_info:
            service.create(test_data)
        assert "Audit log error" in str(exc_info.value)

def test_create_stipend_with_database_error(test_data, db_session, app):
    """Test creating stipend with database error"""
    service = StipendService()
    
    with patch('app.extensions.db.session.commit', side_effect=Exception("Database error")):
        with pytest.raises(Exception) as exc_info:
            service.create(test_data)
        assert "Database error" in str(exc_info.value)

def test_create_stipend_with_rate_limit_exceeded(test_data, db_session, app):
    """Test creating stipend with rate limit exceeded"""
    service = StipendService()
    
    # Create organization first
    org = Organization(name='Test Org')
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id
    
    # Make 11 requests (limit is 10 per minute)
    with pytest.raises(Exception) as exc_info:
        for _ in range(11):
            service.create(test_data)
    assert "Rate limit exceeded" in str(exc_info.value)

def test_invalid_form_submissions(test_data, db_session, app, admin_user):
    """Test various invalid form submission scenarios"""
    invalid_cases = [
        # Missing required fields
        {'name': None, 'organization_id': None, 'application_deadline': None},
        # Invalid field types
        {'name': 123, 'organization_id': 'abc', 'application_deadline': 123456},
        # Exceeding max lengths
        {'name': 'A' * 101, 'summary': 'B' * 501, 'description': 'C' * 2001},
        # Invalid URLs
        {'homepage_url': 'invalid-url'},
        # Invalid boolean values
        {'open_for_applications': 'maybe'},
        # Invalid tag IDs
        {'tags': ['invalid']}
    ]

    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            for case in invalid_cases:
                invalid_data = {**test_data, **case}
                with pytest.raises(ValueError) as exc_info:
                    service.create(invalid_data)
                assert "validation error" in str(exc_info.value).lower()

def test_database_constraint_violations(test_data, db_session, app, admin_user):
    """Test database constraint violations"""
    # Create initial valid stipend
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    valid_data = {
        'name': 'Valid Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test unique constraint violation
            service.create(valid_data)
            with pytest.raises(ValueError) as exc_info:
                service.create(valid_data)
            assert "already exists" in str(exc_info.value)
            
            # Test foreign key constraint violation
            invalid_data = {**valid_data, 'organization_id': 99999}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data)
            assert "foreign key constraint" in str(exc_info.value).lower()

def test_htmx_partial_responses(test_data, db_session, app, admin_user):
    """Test HTMX partial response handling"""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    
    valid_data = {
        'name': 'HTMX Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }
    
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test successful HTMX response
            result = service.create(valid_data, htmx_request=True)
            assert 'hx-redirect' in result.headers
            assert 'hx-trigger' in result.headers
            
            # Test HTMX error response
            invalid_data = {**valid_data, 'name': None}
            with pytest.raises(ValueError) as exc_info:
                service.create(invalid_data, htmx_request=True)
            assert 'hx-trigger' in exc_info.value.headers
            assert 'error' in exc_info.value.headers['hx-trigger']

def test_error_conditions(test_data, db_session, app, admin_user):
    """Test various error conditions"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test database connection failure
            with patch('app.extensions.db.session.commit', side_effect=Exception("DB Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "DB Error" in str(exc_info.value)
                
            # Test audit logging failure
            with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Log Error")):
                with pytest.raises(Exception) as exc_info:
                    service.create(test_data)
                assert "Log Error" in str(exc_info.value)

def test_edge_cases(test_data, db_session, app, admin_user):
    """Test various edge cases"""
    service = StipendService()
    
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
            
            # Test empty string handling
            empty_data = {
                'name': '   ',
                'organization_id': '',
                'application_deadline': ''
            }
            with pytest.raises(ValueError) as exc_info:
                service.create({**test_data, **empty_data})
            assert "cannot be empty" in str(exc_info.value)
            
            # Test maximum values
            max_data = {
                'name': 'A' * 100,
                'summary': 'B' * 500,
                'description': 'C' * 2000,
                'homepage_url': 'http://' + 'a' * 200 + '.com',
                'application_procedure': 'D' * 2000,
                'eligibility_criteria': 'E' * 2000
            }
            result = service.create({**test_data, **max_data})
            assert result is not None
            
            # Test minimum values
            min_data = {
                'name': 'A',
                'summary': 'B',
                'description': 'C',
                'homepage_url': 'http://a.com',
                'application_procedure': 'D',
                'eligibility_criteria': 'E'
            }
            result = service.create({**test_data, **min_data})
            assert result is not None

def test_update_stipend_with_invalid_data(test_data, db_session, app):
    """Test updating stipend with invalid data"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    invalid_data = {
        'name': '',  # Invalid name
        'application_deadline': 'invalid-date'
    }

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.update(stipend.id, invalid_data)
        
    errors = exc_info.value.args[0]
    assert 'name' in errors
    assert 'application_deadline' in errors

def test_delete_stipend_with_dependencies(test_data, db_session, app):
    """Test deleting stipend with dependent records"""
    from app.models.tag import Tag
    
    # Create stipend with tags
    stipend = Stipend(**test_data)
    tag = Tag(name="Test Tag")
    stipend.tags.append(tag)
    db.session.add(stipend)
    db.session.commit()

    service = StipendService()
    
    # Should still be able to delete
    result = service.delete(stipend.id)
    assert result is True
    
    # Verify deletion
    assert Stipend.query.get(stipend.id) is None
    assert Tag.query.get(tag.id) is not None  # Tags should remain

def test_create_stipend_with_duplicate_name(test_data, db_session, app):
    """Test creating stipend with duplicate name"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Create initial stipend
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "already exists" in str(exc_info.value)

def test_create_stipend_with_past_deadline(test_data, db_session, app):
    """Test creating stipend with past deadline"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id
    test_data['application_deadline'] = '2020-01-01 00:00:00'  # Past date

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "must be in the future" in str(exc_info.value)

def test_update_stipend_with_invalid_tags(test_data, db_session, app):
    """Test updating stipend with invalid tags"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    invalid_data = {
        'tags': [9999]  # Non-existent tag
    }

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.update(stipend.id, invalid_data)
        
    assert "Invalid tags" in str(exc_info.value)

def test_create_stipend_with_all_fields(test_data, db_session, app, admin_user):
    # Create an organization first
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()
    test_data['organization_id'] = org.id  # Use the created organization's ID

    # Convert datetime object to string for form submission
    test_data['application_deadline'] = test_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S')

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=test_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        
        service = StipendService()
        result = service.create(form.data)

    # Query the stipend from the session to ensure it's bound
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()

    # Check if the stipend was created successfully with all fields
    assert new_stipend is not None
    for key, value in test_data.items():
        if key == 'application_deadline':
            assert new_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == value
        else:
            assert getattr(new_stipend, key) == value

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.CREATE_STIPEND_SUCCESS.value in messages

def test_create_stipend_with_missing_optional_fields(db_session, app, admin_user):
    # Create an organization first
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()

    test_data = {
        'name': "Test Stipend",
        'application_deadline': datetime.strptime('2023-12-31 23:59:59', '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True,
        'organization_id': org.id  # Add the required organization_id
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=test_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        
        service = StipendService()
        result = service.create(form.data)

    # Query the stipend from the session to ensure it's bound
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()

    # Check if the stipend was created successfully with missing optional fields
    assert new_stipend is not None
    assert new_stipend.name == test_data['name']
    assert new_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == test_data['application_deadline']
    assert new_stipend.open_for_applications is True
    assert new_stipend.summary is None  # Assuming summary is optional
    assert new_stipend.description is None  # Assuming description is optional
    assert new_stipend.organization_id == org.id  # Verify organization association

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.CREATE_STIPEND_SUCCESS.value in messages

def test_create_stipend_with_invalid_date_format(test_data, db_session, app, admin_user):
    # Modify test data with an invalid application_deadline format
    test_data['application_deadline'] = 'invalid-format'  # Different format

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        # Create a form instance and validate it
        form = StipendForm(data=test_data)
        
        service = StipendService()
        result = service.create(form.data)

    # Assert that the stipend was not created due to validation errors
    new_stipend = db_session.query(Stipend).filter_by(name=test_data['name']).first()
    assert new_stipend is None

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.INVALID_DATE_FORMAT.value in messages

def test_update_stipend_with_valid_data(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()
    
    update_data = {
        'name': "Updated Test Stipend",
        'summary': 'Updated summary',
        'description': test_data['description'],
        'homepage_url': test_data['homepage_url'],
        'application_procedure': test_data['application_procedure'],
        'eligibility_criteria': test_data['eligibility_criteria'],
        'application_deadline': datetime.strptime('2024-12-31 23:59:59', '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),  # Ensure it's a string
        'open_for_applications': True
    }
    
    with app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
    
        # Use StipendForm to handle form submission
        form = StipendForm(data=update_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        # Simulate form submission to the edit route
        service = StipendService()
        result = service.update(stipend.id, form.data)
        assert result is not None  # Check service returned a result
        
        db.session.refresh(stipend)
    
    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    
    # Check if the stipend was updated successfully
    assert updated_stipend is not None
    assert updated_stipend.name == "Updated Test Stipend"
    assert updated_stipend.summary == 'Updated summary'
    assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == '2024-12-31 23:59:59'
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.UPDATE_STIPEND_SUCCESS.value in messages

def test_update_stipend_with_invalid_application_deadline_format(test_data, db_session, app, admin_user):
    # Create initial stipend
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()
    
    # Test various invalid date formats
    invalid_formats = [
        '2024-13-32 99:99:99',  # Invalid everything
        '2023-02-30 12:00:00',  # Invalid day
        '2023-04-31 12:00:00',  # Invalid day
        '2023-00-01 12:00:00',  # Invalid month
        '2023-01-00 12:00:00',  # Invalid day
        'invalid-date',         # Completely invalid
        '',                     # Empty string
        None                    # Null value
    ]
    
    for invalid_format in invalid_formats:
        update_data = {
            'name': test_data['name'],
            'application_deadline': invalid_format,
        }
        
        with app.app_context(), app.test_client() as client:
            with app.test_request_context():
                login_user(admin_user)
                
            form = StipendForm(data=update_data)
            service = StipendService()
            
            with pytest.raises(ValueError) as exc_info:
                service.update(stipend.id, form.data)
            
            assert "Invalid date format" in str(exc_info.value)
            
            # Verify stipend was not updated
            updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
            assert updated_stipend.application_deadline == test_data['application_deadline']

def test_update_stipend_open_for_applications(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'name': test_data['name'],  # Add the name field
        'summary': test_data['summary'],
        'description': test_data['description'],
        'homepage_url': test_data['homepage_url'],
        'application_procedure': test_data['application_procedure'],
        'eligibility_criteria': test_data['eligibility_criteria'],
        'application_deadline': test_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': True,
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=update_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        # Simulate form submission after calling update_stipend
        service = StipendService()
        result = service.update(stipend.id, form.data)

    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()

    # Check if the stipend was updated successfully
    assert updated_stipend is not None
    assert updated_stipend.open_for_applications is True

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.UPDATE_STIPEND_SUCCESS.value in messages

def test_update_stipend_open_for_applications_as_string(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'name': test_data['name'],
        'summary': test_data['summary'],
        'description': test_data['description'],
        'homepage_url': test_data['homepage_url'],
        'application_procedure': test_data['application_procedure'],
        'eligibility_criteria': test_data['eligibility_criteria'],
        'application_deadline': test_data['application_deadline'].strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': 'yes',  # Pass as string
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=update_data)
        assert form.validate(), f"Form validation failed: {form.errors}"
        
        # Simulate form submission after calling update_stipend
        service = StipendService()
        result = service.update(stipend.id, form.data)

    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()

    # Check if the stipend was updated successfully
    assert updated_stipend is not None
    assert updated_stipend.open_for_applications is True

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.UPDATE_STIPEND_SUCCESS.value in messages

def test_update_stipend_change_all_fields(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()
 
    update_data = {
        'name': "Updated All Fields",
        'summary': 'Updated summary for all fields',
        'description': 'Updated description for all fields.',
        'homepage_url': 'http://updated.com',
        'application_procedure': 'Updated procedure',
        'eligibility_criteria': 'Updated criteria',
        'application_deadline': datetime.strptime('2025-12-31 23:59:59', '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
        'open_for_applications': '0'
    }
 
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Use StipendForm to handle form submission
        form = StipendForm(data=update_data)
        # Manually process the form to trigger the process_data method
        form.process()

        assert form.validate(), f"Form validation failed: {form.errors}"
        
        # Simulate form submission
        response = client.post(f'/admin/stipends/{stipend.id}/edit', data=form.data, follow_redirects=True)
 
    # Refresh the stipend object to get the updated data from the database
    db_session.refresh(stipend)
 
    # Query the stipend from the session to ensure it's bound
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
 
    # Check if the stipend was updated successfully with all fields changed
    assert updated_stipend is not None
    for key, value in update_data.items():
        if key == 'application_deadline':
            assert updated_stipend.application_deadline.strftime('%Y-%m-%d %H:%M:%S') == value
        else:
            assert getattr(updated_stipend, key) == False if key == 'open_for_applications' else getattr(updated_stipend, key) == value
 
    # Check if the correct flash message was set
    with app.test_request_context():
        assert FlashMessages.UPDATE_STIPEND_SUCCESS.encode() in response.data

def test_update_stipend_with_empty_application_deadline(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    update_data = {
        'name': test_data['name'],
        'application_deadline': '',  # Empty string
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        # Create a form instance and validate it
        form = StipendForm(data=update_data)
        assert not form.validate(), f"Form validation should have failed: {form.errors}"
        
        # Simulate form submission after calling update_stipend
        response = client.post(f'/admin/stipends/{stipend.id}/edit', data=form.data, follow_redirects=True)

    # Assert that the stipend was not updated due to validation errors
    updated_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert updated_stipend.application_deadline == test_data['application_deadline']  # Should remain unchanged

    # Check if the correct flash message was set
    with app.test_request_context():
        assert FlashMessages.INVALID_DATE_FORMAT.encode() in response.data

def test_delete_existing_stipend(test_data, db_session, app, admin_user):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.delete(stipend.id)

    # Assert that the stipend was deleted
    deleted_stipend = db_session.query(Stipend).filter_by(id=stipend.id).first()
    assert deleted_stipend is None

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.DELETE_STIPEND_SUCCESS.value in messages

def test_delete_nonexistent_stipend(app, admin_user):
    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.delete(9999)  # Assuming there's no stipend with ID 9999

    # Check if the correct flash message was set
    with app.test_request_context():
        messages = get_flashed_messages()
        assert FlashMessages.STIPEND_NOT_FOUND.value in messages

def test_get_stipend_by_valid_id(test_data, db_session, app):
    stipend = Stipend(**test_data)
    db_session.add(stipend)
    db_session.commit()

    service = StipendService()
    retrieved_stipend = service.get_by_id(stipend.id)
    assert retrieved_stipend is not None
    assert retrieved_stipend.name == test_data['name']

def test_get_stipend_by_invalid_id(app):
    service = StipendService()
    retrieved_stipend = service.get_by_id(9999)  # Assuming there's no stipend with ID 9999
    assert retrieved_stipend is None

def test_get_all_stipends_with_multiple_entries(test_data, db_session, app):
    stipend1 = Stipend(**test_data)
    stipend2 = Stipend(name="Another Test Stipend", summary="Summary of another stipend")
    db_session.add(stipend1)
    db_session.add(stipend2)
    db_session.commit()

    service = StipendService()
    all_stipends = service.get_all()
    assert len(all_stipends) == 2
    assert any(s.name == test_data['name'] for s in all_stipends)

def test_get_all_stipends_with_no_entries(app):
    service = StipendService()
    all_stipends = service.get_all()
    assert len(all_stipends) == 0

def test_create_stipend_with_max_length_fields(test_data, db_session, app, admin_user):
    """Test creating stipend with maximum length fields"""
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    # Set max length values
    test_data.update({
        'name': 'A' * 100,  # Max length
        'summary': 'B' * 500,
        'description': 'C' * 2000,
        'homepage_url': 'http://' + 'a' * 200 + '.com',
        'application_procedure': 'D' * 2000,
        'eligibility_criteria': 'E' * 2000,
        'organization_id': org.id
    })

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(test_data)
        
        # Verify all fields were saved correctly
        stipend = Stipend.query.filter_by(name=test_data['name']).first()
        assert stipend is not None
        assert len(stipend.name) == 100
        assert len(stipend.summary) == 500
        assert len(stipend.description) == 2000

def test_create_stipend_with_minimal_data(db_session, app, admin_user):
    """Test creating stipend with only required fields"""
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    
    minimal_data = {
        'name': 'Minimal Stipend',
        'organization_id': org.id,
        'application_deadline': '2025-12-31 23:59:59'
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(minimal_data)
        
        # Verify stipend was created with minimal data
        stipend = Stipend.query.filter_by(name='Minimal Stipend').first()
        assert stipend is not None
        assert stipend.summary is None
        assert stipend.description is None

def test_update_stipend_with_empty_fields(test_data, db_session, app, admin_user):
    """Test updating stipend with empty optional fields"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    update_data = {
        'name': 'Updated Stipend',
        'summary': '',
        'description': '',
        'organization_id': stipend.organization_id
    }

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.update(stipend.id, update_data)
        
        # Verify update
        updated_stipend = Stipend.query.get(stipend.id)
        assert updated_stipend.name == 'Updated Stipend'
        assert updated_stipend.summary is None
        assert updated_stipend.description is None

def test_stipend_service_rate_limiting(test_data, app):
    """Test rate limiting in stipend service"""
    service = StipendService()
    
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Make 11 requests (limit is 10 per minute)
    with pytest.raises(Exception) as exc_info:
        for i in range(11):
            service.create(test_data)
            
    assert "Rate limit exceeded" in str(exc_info.value)

def test_stipend_service_audit_logging(test_data, db_session, app, admin_user):
    """Test audit logging in stipend service"""
    from app.models.audit_log import AuditLog
    
    # Create organization first
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    with app.app_context(), app.test_client() as client:
        with app.test_request_context():
            login_user(admin_user)
        
        service = StipendService()
        result = service.create(test_data)
        
        # Verify audit log was created
        log = AuditLog.query.filter_by(object_type='Stipend').first()
        assert log is not None
        assert log.action == 'create'
        assert log.object_id == result.id

def test_create_stipend_with_invalid_organization(test_data, db_session, app):
    """Test creating stipend with invalid organization"""
    test_data['organization_id'] = 9999  # Non-existent organization
    
    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "Invalid organization" in str(exc_info.value)

def test_update_stipend_with_invalid_data(test_data, db_session, app):
    """Test updating stipend with invalid data"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    invalid_data = {
        'name': '',  # Invalid name
        'application_deadline': 'invalid-date'
    }

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.update(stipend.id, invalid_data)
        
    errors = exc_info.value.args[0]
    assert 'name' in errors
    assert 'application_deadline' in errors

def test_delete_stipend_with_dependencies(test_data, db_session, app):
    """Test deleting stipend with dependent records"""
    from app.models.tag import Tag
    
    # Create stipend with tags
    stipend = Stipend(**test_data)
    tag = Tag(name="Test Tag")
    stipend.tags.append(tag)
    db.session.add(stipend)
    db.session.commit()

    service = StipendService()
    
    # Should still be able to delete
    result = service.delete(stipend.id)
    assert result is True
    
    # Verify deletion
    assert Stipend.query.get(stipend.id) is None
    assert Tag.query.get(tag.id) is not None  # Tags should remain

def test_create_stipend_with_duplicate_name(test_data, db_session, app):
    """Test creating stipend with duplicate name"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Create initial stipend
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "already exists" in str(exc_info.value)

def test_create_stipend_with_past_deadline(test_data, db_session, app):
    """Test creating stipend with past deadline"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id
    test_data['application_deadline'] = '2020-01-01 00:00:00'  # Past date

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.create(test_data)
        
    assert "must be in the future" in str(exc_info.value)

def test_update_stipend_with_invalid_tags(test_data, db_session, app):
    """Test updating stipend with invalid tags"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    invalid_data = {
        'tags': [9999]  # Non-existent tag
    }

    service = StipendService()
    
    with pytest.raises(ValueError) as exc_info:
        service.update(stipend.id, invalid_data)
        
    assert "Invalid tags" in str(exc_info.value)

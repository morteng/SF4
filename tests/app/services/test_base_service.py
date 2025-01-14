import pytest
from unittest.mock import Mock, patch
from app.services.base_service import BaseService
from app.models.stipend import Stipend
from app.extensions import db
from datetime import datetime

@pytest.fixture
def base_service():
    return BaseService(Stipend)

def test_base_service_create(base_service, db_session):
    test_data = {
        'name': 'Test Stipend',
        'application_deadline': datetime.utcnow()
    }
    
    result = base_service.create(test_data)
    assert result is not None
    assert result.name == 'Test Stipend'
    assert db_session.query(Stipend).count() == 1

def test_base_service_create_validation_error(base_service):
    with pytest.raises(ValueError):
        base_service.create({})  # Missing required fields

def test_base_service_update(base_service, db_session):
    # Create initial record
    stipend = Stipend(name='Old Name', application_deadline=datetime.utcnow())
    db_session.add(stipend)
    db_session.commit()
    
    # Update record
    update_data = {'name': 'New Name'}
    updated = base_service.update(stipend.id, update_data)
    assert updated.name == 'New Name'

def test_base_service_delete(base_service, db_session):
    stipend = Stipend(name='Test Delete', application_deadline=datetime.utcnow())
    db_session.add(stipend)
    db_session.commit()
    
    base_service.delete(stipend.id)
    assert db_session.query(Stipend).count() == 0

def test_base_service_rate_limiting(base_service):
    # Test rate limiting for create operations
    with patch('app.extensions.limiter') as mock_limiter:
        base_service.create({'name': 'Test', 'application_deadline': datetime.utcnow()})
        mock_limiter.limit.assert_called_once()

def test_base_service_audit_logging(base_service, db_session):
    with patch('app.models.audit_log.AuditLog.create') as mock_audit:
        test_data = {
            'name': 'Audit Test',
            'application_deadline': datetime.utcnow()
        }
        base_service.create(test_data)
        mock_audit.assert_called()

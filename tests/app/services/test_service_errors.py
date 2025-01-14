import pytest
from unittest.mock import patch
from app.services.stipend_service import StipendService
from app.models import Stipend
from app.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

def test_create_stipend_database_error(test_data):
    """Test handling of database errors during stipend creation"""
    service = StipendService()
    
    with patch('app.extensions.db.session.commit', side_effect=SQLAlchemyError("Database error")):
        with pytest.raises(SQLAlchemyError):
            service.create(test_data)
            
        # Verify rollback occurred
        assert db.session.is_active
        assert Stipend.query.count() == 0

def test_update_stipend_not_found(test_data):
    """Test updating a non-existent stipend"""
    service = StipendService()
    non_existent_id = 9999
    
    with pytest.raises(ValueError) as exc_info:
        service.update(non_existent_id, test_data)
        
    assert "not found" in str(exc_info.value).lower()

def test_delete_stipend_not_found():
    """Test deleting a non-existent stipend"""
    service = StipendService()
    non_existent_id = 9999
    
    with pytest.raises(ValueError) as exc_info:
        service.delete(non_existent_id)
        
    assert "not found" in str(exc_info.value).lower()

def test_rate_limiting_exceeded(test_data):
    """Test rate limiting in service operations"""
    service = StipendService()
    
    # Mock rate limiter to always fail
    with patch('app.extensions.limiter.limit', side_effect=Exception("Rate limit exceeded")):
        with pytest.raises(Exception) as exc_info:
            service.create(test_data)
            
        assert "Rate limit exceeded" in str(exc_info.value)

def test_audit_logging_failure(test_data):
    """Test service continues working when audit logging fails"""
    service = StipendService()
    
    with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Audit log error")):
        result = service.create(test_data)
        assert result is not None  # Service should still work
        assert Stipend.query.count() == 1

def test_validation_error_handling():
    """Test validation error handling in service layer"""
    service = StipendService()
    invalid_data = {
        'name': '',  # Invalid name
        'application_deadline': 'invalid-date'
    }
    
    with pytest.raises(ValueError) as exc_info:
        service.create(invalid_data)
        
    errors = exc_info.value.args[0]
    assert 'name' in errors
    assert 'application_deadline' in errors

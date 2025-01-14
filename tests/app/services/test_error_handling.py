import pytest
from unittest.mock import patch
from app.services.base_service import BaseService
from app.models.stipend import Stipend
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture
def error_service():
    return BaseService(Stipend)

def test_database_connection_error(error_service):
    with patch('app.extensions.db.session.commit', side_effect=SQLAlchemyError("Connection failed")):
        with pytest.raises(SQLAlchemyError):
            error_service.create({'name': 'Test', 'application_deadline': '2025-01-01'})

def test_validation_error(error_service):
    with pytest.raises(ValueError):
        error_service.create({'invalid': 'data'})

def test_rate_limit_error(error_service):
    with patch('app.extensions.limiter.limit', side_effect=Exception("Rate limit exceeded")):
        with pytest.raises(Exception):
            error_service.create({'name': 'Test', 'application_deadline': '2025-01-01'})

def test_audit_log_error(error_service):
    with patch('app.models.audit_log.AuditLog.create', side_effect=Exception("Audit log failed")):
        # Should still complete operation even if audit logging fails
        result = error_service.create({'name': 'Test', 'application_deadline': '2025-01-01'})
        assert result is not None

import pytest
from flask import url_for
from app.models import AuditLog

def test_audit_log_table_exists(db_session):
    """Test that audit_log table exists and can be used"""
    # Create test audit log entry
    log = AuditLog(
        user_id=1,
        action='test_action',
        details='Test details'
    )
    db_session.add(log)
    db_session.commit()
    
    # Verify entry exists
    assert db_session.query(AuditLog).count() == 1

def test_invalid_stipend_data(client, db_session):
    """Test handling of invalid stipend data"""
    # Attempt to create stipend with missing required fields
    response = client.post(url_for('admin.stipend.create'), data={
        'name': '',  # Required field
        'summary': 'Test summary'
    })
    
    assert response.status_code == 400
    assert b'This field is required' in response.data

def test_rate_limiting(client):
    """Test rate limiting functionality"""
    responses = []
    for i in range(11):  # Assuming limit is 10 requests/minute
        response = client.get(url_for('public.index'))
        responses.append(response.status_code)
    
    assert 429 in responses  # Should get rate limited
    assert responses.count(200) == 10  # First 10 should succeed

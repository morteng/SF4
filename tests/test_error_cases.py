import pytest
from flask import current_app
from app.models import AuditLog, User
from app.extensions import db

def test_audit_log_table_exists(client):
    """Test that audit_log table exists"""
    inspector = db.inspect(db.engine)
    assert inspector.has_table('audit_log'), "audit_log table does not exist"

def test_audit_log_create_without_table(client):
    """Test audit log creation when table is missing"""
    # Drop audit_log table for this test
    db.engine.execute("DROP TABLE IF EXISTS audit_log")
    
    with pytest.raises(RuntimeError) as excinfo:
        AuditLog.create(user_id=1, action="test")
    assert "Audit log table not found" in str(excinfo.value)

def test_database_constraint_violation(client):
    """Test handling of database constraint violations"""
    # Try to create user with duplicate username
    user1 = User(username="testuser", email="test1@example.com")
    db.session.add(user1)
    db.session.commit()
    
    user2 = User(username="testuser", email="test2@example.com")
    db.session.add(user2)
    
    with pytest.raises(Exception):
        db.session.commit()
    
    # Verify rollback
    db.session.rollback()
    assert User.query.count() == 1

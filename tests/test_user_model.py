import pytest
from datetime import datetime
from freezegun import freeze_time
from app.models.user import User

def test_security_columns(db_session):
    """Validate security-related database columns exist and function"""
    with freeze_time("2025-01-26 01:00:00"):
        user = User(
            username='test_user',
            email='test@example.com',
            password_hash='testhash',
            confirmed_at=datetime.utcnow(),
            last_failed_login=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()

    stored_user = User.query.filter_by(username='test_user').first()
    
    # Validate required security fields
    assert stored_user.confirmed_at == datetime(2025, 1, 26, 1, 0), "Confirmed_at timestamp mismatch"
    assert stored_user.last_failed_login == datetime(2025, 1, 26, 1, 0), "Last_failed_login timestamp mismatch"
    assert isinstance(stored_user.confirmed_at, datetime), "Confirmed_at should be datetime type"
    assert isinstance(stored_user.last_failed_login, datetime), "Last_failed_login should be datetime type"

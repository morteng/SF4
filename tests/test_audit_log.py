import pytest
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash
from flask import url_for, Flask
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.notification import Notification
from app.constants import NotificationType

def test_audit_log_creation():
    """Test audit log creation with proper request context"""
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    # Initialize extensions
    from app.extensions import db
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create test user
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        # Test audit log creation
        log = AuditLog.create(
            user_id=test_user.id,
            action="test_action",
            details="Test details"
        )
        
        # Assertions
        assert log.id is not None
        assert log.action == "test_action"
        assert log.user_id == test_user.id
        assert log.details == "Test details"
        
        # Clean up
        db.session.remove()
        db.drop_all()

def test_audit_log_missing_action():
    """Test audit log creation with missing required field"""
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    from app.extensions import db
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        with pytest.raises(ValueError):
            AuditLog.create(
                user_id=test_user.id,
                action=None
            )
        
        db.session.remove()
        db.drop_all()

def test_audit_log_object_type_without_id():
    """Test audit log creation with object type but no ID"""
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    from app.extensions import db
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        with pytest.raises(ValueError):
            AuditLog.create(
                user_id=test_user.id,
                action="test_action",
                object_type="TestType"
            )
        
        db.session.remove()
        db.drop_all()

def test_audit_log_with_object_id():
    """Test audit log creation with object ID"""
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    from app.extensions import db
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        
        log = AuditLog.create(
            user_id=test_user.id,
            action="test_action",
            details="Test details",
            object_type="TestType",
            object_id=123
        )
        
        assert log.object_type == "TestType"
        assert log.object_id == 123
        
        db.session.remove()
        db.drop_all()


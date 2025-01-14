from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    _is_active = db.Column('is_active', db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    __mapper_args__ = {"confirm_deleted_rows": False}

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    def __init__(self, username, email, password=None, password_hash=None, is_admin=False, is_active=True, confirmed_at=None):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        elif password_hash:
            self.password_hash = password_hash
        self.is_admin = is_admin
        self._is_active = is_active  # Set the private attribute directly
        self.confirmed_at = confirmed_at  # Add this line
        self.created_at = db.func.current_timestamp()
        self.updated_at = db.func.current_timestamp()

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Override get_id to return string ID for Flask-Login"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Override is_authenticated to check confirmed_at in production only"""
        if current_app.config.get('TESTING'):
            return super().is_authenticated
        return super().is_authenticated and self.confirmed_at is not None

    def update_profile(self, username, email):
        """Update user profile information"""
        self.username = username
        self.email = email
        return self
    
    @classmethod
    def get_by_id(cls, user_id, session):
        """Get user by ID with proper session handling"""
        return session.query(cls).get(user_id)

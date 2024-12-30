from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
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

    def __init__(self, username, email, password=None, is_admin=False):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        self.is_admin = is_admin
        self.is_active = True  # This will now use the property setter
        self.created_at = db.func.current_timestamp()
        self.updated_at = db.func.current_timestamp()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_profile(self, username, email):
        """Update user profile information"""
        self.username = username
        self.email = email
        return self
    
    # Flask-Login required properties and methods
    @property
    def is_active(self):
        """Return whether the user is active."""
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        """Set the user's active status."""
        if not isinstance(value, bool):
            raise ValueError("is_active must be a boolean")
        self._is_active = value

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @classmethod
    def get_by_id(cls, user_id, session):
        """Get user by ID with proper session handling"""
        return session.query(cls).get(user_id)

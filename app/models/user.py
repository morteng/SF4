from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets  # Built into Python, no extra dependencies needed
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    auth_token = db.Column(db.String(64), unique=True)  # Add this field
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Set the user's password with validation."""
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        """Generate a simple random token."""
        self.auth_token = secrets.token_hex(32)
        db.session.commit()
        return self.auth_token

    @staticmethod
    def verify_auth_token(token):
        """Verify a token and return the corresponding user."""
        return User.query.filter_by(auth_token=token).first()

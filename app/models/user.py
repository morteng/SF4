from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db  # Import db from extensions instead of creating a new instance

class User(db.Model):
    """
    Represents a user in the application.
    
    Attributes:
        id (int): Unique identifier for the user.
        username (str): Username of the user.
        email (str): Email address of the user.
        password_hash (str): Hashed password of the user.
        is_admin (bool): Indicates if the user is an admin.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp when the user was last updated.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def set_password(self, password):
        """
        Sets the user's password by hashing it.
        
        Args:
            password (str): The plain text password to be hashed and stored.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Checks if the provided password matches the stored hash.
        
        Args:
            password (str): The plain text password to be checked against the stored hash.
            
        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

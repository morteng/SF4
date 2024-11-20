from flask_sqlalchemy import SQLAlchemy

def init_extensions(app):
    # Ensure db is already initialized in __init__.py
    from .models import db  # Import the db instance from models/__init__.py
    # Other extensions can be initialized here if needed

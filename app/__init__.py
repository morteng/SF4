from .factory import create_app
from .models.base_model import db

__all__ = ['create_app', 'db']  # Expose both create_app and db

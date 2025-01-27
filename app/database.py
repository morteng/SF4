from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
Base = db.Model

__all__ = ['Base', 'db']

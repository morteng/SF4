from flask_sqlalchemy import SQLAlchemy

# db is already defined and initialized in app/__init__.py, so no need to re-initialize it here.
def init_extensions(app):
    # Ensure that db.init_app(app) is not called here again.
    pass

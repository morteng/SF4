from flask import Flask
from .config import config_by_name  # Corrected import statement
from flask_migrate import Migrate
import os  # Import the os module
from .extensions import db, login_manager, init_extensions, init_admin_user

migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Print environment variables for debugging
    print(f"FLASK_CONFIG: {os.getenv('FLASK_CONFIG')}")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

    config_class = config_by_name.get(os.getenv('FLASK_CONFIG', 'default'))
    app.config.from_object(config_class)

    # Print the database URI being used
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debugging line

    init_extensions(app)
    
    with app.app_context():
        db.create_all()  # Create the database tables if they don't exist
        init_admin_user()  # Initialize admin user within the application context
        init_routes(app)

    return app


def init_routes(app):
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.visitor_routes import visitor_bp  # Ensure this matches the file name

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(visitor_bp)  # No prefix for visitor routes

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

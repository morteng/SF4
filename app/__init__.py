import os
from flask import Flask
from app.extensions import db
from app.config import config_by_name
from app.services.user_service import ensure_default_admin_exists
from flask_login import LoginManager
from dotenv import load_dotenv

# Import your blueprints
from app.routes.admin_bot import admin_bot_bp
from app.routes.admin_org import admin_org_bp
from app.routes.admin_stipend import admin_stipend_bp
from app.routes.admin_tag import admin_tag_bp
from app.routes.admin_user import admin_user_bp

def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name (str, optional): The name of the configuration to use. Defaults to None.

    Returns:
        Flask: The configured Flask application.
    """
    load_dotenv()
    
    # Print environment variables for debugging
    print(f"FLASK_CONFIG: {os.getenv('FLASK_CONFIG')}")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    print(f"ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME')}")
    print(f"ADMIN_PASSWORD: {os.getenv('ADMIN_PASSWORD')}")
    print(f"ADMIN_EMAIL: {os.getenv('ADMIN_EMAIL')}")

    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load a user by their ID.

        Args:
            user_id (int): The ID of the user to load.

        Returns:
            User: The loaded user object.
        """
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')
    
    with app.app_context():
        print(f"Creating Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Ensure the instance directory exists
        db_file_path = os.path.join(app.instance_path, 'site.db')
        if not os.path.exists(os.path.dirname(db_file_path)):
            os.makedirs(os.path.dirname(db_file_path))
        
        # Create the database file if it doesn't exist
        if not os.path.isfile(db_file_path):
            with open(db_file_path, 'w') as f:
                pass  # Creating an empty file

        print(f"Database file path: {db_file_path}")
        print(f"Instance path: {app.instance_path}")
        print(f"Does directory exist? {os.path.exists(os.path.dirname(db_file_path))}")
        print(f"Does database file exist? {os.path.isfile(db_file_path)}")
        print(f"File permissions: {oct(os.stat(db_file_path).st_mode & 0o777)}")

        try:
            db.create_all()
        except Exception as e:
            print(f"Error creating tables: {e}")
        
        # Ensure default admin user exists
        ensure_default_admin_exists()
    
    return app

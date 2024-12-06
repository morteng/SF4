from dotenv import load_dotenv
import os
from flask import Flask
from app.extensions import db
from app.config import config_by_name
from app.services.user_service import ensure_default_admin_exists
from flask_login import LoginManager

# Import your blueprints
from app.routes.admin_bot import admin_bot_bp
from app.routes.admin_org import admin_org_bp
from app.routes.admin_stipend import admin_stipend_bp
from app.routes.admin_tag import admin_tag_bp
from app.routes.admin_user import admin_user_bp

def create_app(config_name=None):
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
        instance_path = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].split('///')[1])
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        
        # Create the database file if it doesn't exist
        db_file_path = app.config['SQLALCHEMY_DATABASE_URI'].split('///')[1]
        if not os.path.isfile(db_file_path):
            with open(db_file_path, 'w') as f:
                pass  # Creating an empty file

        db.create_all()
        
        # Ensure default admin user exists
        ensure_default_admin_exists()
    
    return app

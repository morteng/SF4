from dotenv import load_dotenv
import os
from flask import Flask
from app.extensions import db
from app.config import config_by_name
from app.services.user_service import ensure_default_admin_exists
from flask_login import LoginManager  # Added this import

# Import your blueprints
from app.routes.admin_bot import admin_bot_bp
from app.routes.admin_org import admin_org_bp
from app.routes.admin_stipend import admin_stipend_bp
from app.routes.admin_tag import admin_tag_bp
from app.routes.admin_user import admin_user_bp

def create_app(config_name=None):
    load_dotenv()
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()  # This line is now correct
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
        db.create_all()
        
        # Ensure default admin user exists
        ensure_default_admin_exists()
    
    return app

from dotenv import load_dotenv
import os
from flask import Flask
from flask_login import LoginManager
from app.extensions import db
from app.config import config_by_name
from app.services.user_service import ensure_default_admin_exists
from app.routes.admin import admin_bp
from app.routes.user_routes import user_bp
from app.routes.visitor_routes import visitor_bp

def create_app(config_name=None):
    load_dotenv()
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
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(visitor_bp)
    
    with app.app_context():
        db.create_all()
        
        # Ensure default admin user exists
        ensure_default_admin_exists()
    
    return app

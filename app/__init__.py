# app/__init__.py
from flask import Flask
from app.extensions import db, login_manager
from app.config import config_by_name
from dotenv import load_dotenv
import os

def create_app(config_name=None, instance_path=None):
    # Load environment variables from .env file
    load_dotenv()
    
    # Determine the config name from environment variable or default to 'development'
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__, instance_path=instance_path)
    app.config.from_object(config_by_name[config_name])
    
    print(f"Config name: {config_name}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register admin-related blueprints directly with their own prefixes
    from app.routes.admin.bot_routes import admin_bot_bp
    from app.routes.admin.organization_routes import org_bp
    from app.routes.admin.stipend_routes import admin_stipend_bp
    from app.routes.admin.tag_routes import tag_bp
    from app.routes.admin.user_routes import user_bp
    
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(user_bp, url_prefix='/admin/users')
    
    # Register user blueprint
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # Register visitor blueprint
    from app.routes.visitor_routes import visitor_bp
    app.register_blueprint(visitor_bp)
    
    return app

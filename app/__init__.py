from flask import Flask
from flask_migrate import Migrate  # Correct import for Migrate
from app.extensions import db, login_manager, init_extensions
from app.routes.admin.stipend_routes import admin_stipend_bp
from app.routes.admin.tag_routes import admin_tag_bp
from app.routes.admin.organization_routes import admin_org_bp
from app.routes.admin.user_routes import admin_user_bp
from app.routes.admin.bot_routes import admin_bot_bp
from app.routes.public_user_routes import public_user_bp
from app.routes.public_bot_routes import public_bot_bp
from app.routes.user.user_routes import user_bp
from app.config import get_config  # Import get_config from app.config
from dotenv import load_dotenv  # Import load_dotenv to load environment variables

def create_app(config_name='default'):
    load_dotenv()  # Load environment variables from .env file
    app = Flask(__name__)
    
    # Load configuration using the get_config function
    config_class = get_config(config_name)
    if config_class:
        app.config.from_object(config_class)
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")
    
    # Initialize extensions
    init_extensions(app)
    migrate = Migrate(app, db)  # Initialize Migrate here
    
    # Register blueprints
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(public_user_bp, url_prefix='/')
    app.register_blueprint(public_bot_bp, url_prefix='/bots')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    print("Blueprints registered successfully.")
    
    return app

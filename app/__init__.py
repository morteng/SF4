from flask import Flask, migrate
from app.extensions import db, login_manager
from app.routes.admin.stipend_routes import admin_stipend_bp
from app.routes.admin.tag_routes import admin_tag_bp
from app.routes.admin.organization_routes import admin_org_bp
from app.routes.admin.user_routes import admin_user_bp
from app.routes.admin.bot_routes import admin_bot_bp
from app.routes.public_user_routes import public_user_bp
from app.routes.public_bot_routes import public_bot_bp
from app.routes.user.user_routes import user_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration using the get_config function
    config_class = get_config(config_name)
    if config_class:
        app.config.from_object(config_class)
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(public_user_bp, url_prefix='/')
    
    print("Blueprints registered successfully.")
    
    return app

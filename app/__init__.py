from dotenv import load_dotenv
import os
from .config import get_config  # Use get_config function instead of importing Config directly
from flask import Flask

def create_app(config_name=None):
    load_dotenv()
    
    print("Environment variables:", dict(os.environ))  # Add this line to verify .env loading
    
    app = Flask(__name__)
    config = get_config(config_name or os.getenv('FLASK_CONFIG', 'default'))
    app.config.from_object(config)
    
    # Initialize extensions and blueprints here
    from .extensions import db
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Ensure tables are created

    # Register blueprints
    from .routes.public_user_routes import public_user_bp
    from .routes.public_bot_routes import public_bot_bp
    from .routes.admin.bot_routes import admin_bot_bp
    from .routes.admin.organization_routes import org_bp
    from .routes.admin.stipend_routes import stipend_bp
    from .routes.admin.tag_routes import tag_bp
    from .routes.admin.user_routes import admin_user_bp

    app.register_blueprint(public_user_bp)
    app.register_blueprint(public_bot_bp)
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')

    return app

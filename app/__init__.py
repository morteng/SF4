from flask import Flask
from config import Config
from app.extensions import db

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    from app.routes.admin import admin_bp
    from app.routes.public_bot_routes import public_bot_bp
    from app.routes.public_user_routes import public_user_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(public_bot_bp)
    app.register_blueprint(public_user_bp)

    # Ensure all admin blueprints are registered
    from app.routes.admin.auth_routes import auth_bp as admin_auth_bp
    from app.routes.admin.bot_routes import bot_bp as admin_bot_bp
    from app.routes.admin.organization_routes import org_bp as admin_org_bp
    from app.routes.admin.stipend_routes import stipend_bp as admin_stipend_bp
    from app.routes.admin.tag_routes import tag_bp as admin_tag_bp
    from app.routes.admin.user_routes import user_bp as admin_user_bp

    app.register_blueprint(admin_auth_bp, url_prefix='/admin/auth')
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')

    return app

def init_extensions(app):
    db.init_app(app)

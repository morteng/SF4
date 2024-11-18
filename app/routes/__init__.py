from flask import Blueprint

# Import individual admin route blueprints
from .admin.bot_routes import bot_bp as admin_bot_bp
from .admin.organization_routes import organization_bp as admin_organization_bp
from .admin.stipend_routes import stipend_bp as admin_stipend_bp
from .admin.tag_routes import tag_bp as admin_tag_bp
from .admin.user_routes import user_bp as admin_user_bp

def register_blueprints(app):
    # Register other blueprints if any
    from .public_bot_routes import public_bot_bp
    from .public_user_routes import public_user_bp
    app.register_blueprint(public_bot_bp)
    app.register_blueprint(public_user_bp)

    # Register admin blueprints
    app.register_blueprint(admin_bot_bp, url_prefix='/admin')
    app.register_blueprint(admin_organization_bp, url_prefix='/admin')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin')
    app.register_blueprint(admin_user_bp, url_prefix='/admin')

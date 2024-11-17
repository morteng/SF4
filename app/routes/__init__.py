from flask import Blueprint

from .admin.tag_routes import tag_bp
from .admin.organization_routes import org_bp 
from .admin.stipend_routes import stipend_bp
from .admin.bot_routes import admin_bot_bp  
from .admin.user_routes import admin_user_bp 

# Import new public route blueprints
from .public_bot_routes import public_bot_bp
from .public_user_routes import public_user_bp

def register_blueprints(app):
    # Register admin blueprints
    app.register_blueprint(tag_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(stipend_bp) 
    app.register_blueprint(admin_bot_bp)
    app.register_blueprint(admin_user_bp)

    # Register public blueprints
    app.register_blueprint(public_bot_bp)
    app.register_blueprint(public_user_bp)

# Add more blueprints here if needed

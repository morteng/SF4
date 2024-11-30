from flask import Blueprint

# Import individual admin route modules
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp as admin_org_bp
from .stipend_routes import admin_stipend_bp
from .tag_routes import tag_bp as admin_tag_bp
from .user_routes import user_bp as admin_user_bp
from .dashboard_routes import admin_dashboard_bp
from .auth_routes import auth_bp  # Import the auth blueprint

# Register blueprints
def register_admin_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/admin/auth')  # Register the auth blueprint
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin/dashboard')

from flask import Blueprint

# Import individual admin route modules
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp as admin_org_bp
from .stipend_routes import admin_stipend_bp
from .tag_routes import tag_bp as admin_tag_bp
from .user_routes import user_bp as admin_user_bp
from .dashboard_routes import admin_dashboard_bp  # Import the new blueprint

# Register blueprints
def register_admin_blueprints(app):
    app.register_blueprint(admin_bot_bp, url_prefix='/bots')
    app.register_blueprint(admin_org_bp, url_prefix='/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/users')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')  # Register the new blueprint

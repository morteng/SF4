from .auth_routes import auth_bp as admin_auth_bp
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp as admin_org_bp  # Corrected import statement
from .stipend_routes import admin_stipend_bp  # Corrected import statement
from .tag_routes import tag_bp as admin_tag_bp
from .user_routes import user_bp as admin_user_bp

def init_routes(app):
    app.register_blueprint(admin_auth_bp, url_prefix='/admin/auth')
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')

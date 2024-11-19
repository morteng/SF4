from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

def init_routes(app):
    from .bot_routes import admin_bot_bp
    from .organization_routes import admin_org_bp
    from .stipend_routes import admin_stipend_bp
    from .tag_routes import admin_tag_bp
    from .user_routes import admin_user_bp

    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')

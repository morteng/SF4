from flask import render_template
from .admin.bot_routes import admin_bot_bp
from .admin.organization_routes import admin_org_bp
from .admin.stipend_routes import admin_stipend_bp
from .admin.tag_routes import admin_tag_bp
from .admin.user_routes import admin_user_bp
from .public_user_routes import public_user_bp

def init_routes(app):
    # Register blueprints
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')
    app.register_blueprint(public_user_bp, url_prefix='/user')

    # Add the root route
    @app.route('/')
    def index():
        return render_template('index.html')

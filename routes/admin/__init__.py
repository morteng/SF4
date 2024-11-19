from flask import Blueprint
from .stipend_routes import admin_stipend_bp
from .organization_routes import admin_org_bp
from .bot_routes import admin_bot_bp

# Ensure the correct path to tag_routes.py
from .tag_routes import admin_tag_bp

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def init_routes(app):
    app.register_blueprint(admin_stipend_bp)
    print(f"Registered blueprint: {admin_stipend_bp.name}")

    app.register_blueprint(admin_org_bp)
    print(f"Registered blueprint: {admin_org_bp.name}")

    app.register_blueprint(admin_tag_bp)
    print(f"Registered blueprint: {admin_tag_bp.name}")

    app.register_blueprint(admin_bot_bp)
    print(f"Registered blueprint: {admin_bot_bp.name}")

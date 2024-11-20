from flask import Blueprint

# Import individual admin route modules
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp as admin_org_bp
from .stipend_routes import admin_stipend_bp
from .tag_routes import tag_bp as admin_tag_bp
from .user_routes import user_bp as admin_user_bp

# No need to register blueprints here, they will be registered in the main routes/__init__.py

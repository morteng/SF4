from .admin.bot_routes import admin_bot_bp
from .admin.organization_routes import admin_organization_bp
from .admin.stipend_routes import admin_stipend_bp
from .admin.tag_routes import admin_tag_bp
from .admin.user_routes import admin_user_bp
from .public_bot_routes import public_bot_bp
from .public_user_routes import public_user_bp

# Combine all blueprints into a single list for easy registration
all_blueprints = [
    admin_bot_bp,
    admin_organization_bp,
    admin_stipend_bp,
    admin_tag_bp,
    admin_user_bp,
    public_bot_bp,
    public_user_bp
]

from .admin import init_routes as admin_init_routes
from .public_bot_routes import public_bot_bp
from .public_user_routes import public_user_bp

def init_routes(app):
    # Initialize admin routes
    admin_init_routes(app)

    # Register additional blueprints if needed

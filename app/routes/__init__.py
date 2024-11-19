from .admin import admin_bp
from .user import user_bp  # Uncommented and added
from .public_bot_routes import public_bot_bp  # Added
from .public_user_routes import public_user_bp  # Added

def init_routes(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp)  # Added
    app.register_blueprint(public_bot_bp, url_prefix='/bots')  # Added
    app.register_blueprint(public_user_bp)  # Added

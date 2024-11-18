from .admin_routes import bp as admin_bp
from .public_bot_routes import public_bot_bp
from .public_user_routes import public_user_bp

# Register blueprints with the app in your create_app function
def register_blueprints(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(public_bot_bp, url_prefix='/bots')
    app.register_blueprint(public_user_bp, url_prefix='/users')

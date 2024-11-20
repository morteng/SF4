from flask import Blueprint

# Import and register other blueprints here
from .admin import admin_bp
from .user_routes import user_bp

# Register the public routes
from .public_routes import public_bp

def init_routes(app):
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

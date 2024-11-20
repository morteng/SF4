from flask import Blueprint

# Importing blueprints
from .admin import admin_bp
from .public_user_routes import public_bp
from .user_routes import user_bp

def init_routes(app):
    # Registering blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(public_bp)
    app.register_blueprint(user_bp, url_prefix='/user')

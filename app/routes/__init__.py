from .admin import admin_bp
# from .user import user_bp  # Commented out or removed

def init_routes(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')
    # app.register_blueprint(user_bp)  # Commented out or removed

from .admin import register_admin_blueprints

def register_blueprints(app):
    # Only register blueprints that haven't been registered yet
    if 'user' not in app.blueprints:
        from app.routes.user_routes import user_bp
        app.register_blueprint(user_bp)
    
    if 'public' not in app.blueprints:
        from app.routes.public_routes import public_bp
        app.register_blueprint(public_bp)
    
    # Add admin blueprint registration check
    if 'admin' not in app.blueprints:
        from app.routes.admin import register_admin_blueprints
        register_admin_blueprints(app)

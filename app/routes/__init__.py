from .admin import register_admin_blueprints

def register_blueprints(app):
    # Track which blueprints have been registered
    registered_blueprints = set(app.blueprints.keys())
    
    # Register user blueprint
    if 'user' not in registered_blueprints:
        from app.routes.user_routes import user_bp
        app.register_blueprint(user_bp)
        registered_blueprints.add('user')
    
    # Register public blueprint
    if 'public' not in registered_blueprints:
        from app.routes.public_routes import public_bp
        app.register_blueprint(public_bp)
        registered_blueprints.add('public')
    
    # Register admin blueprints
    if 'admin' not in registered_blueprints:
        from app.routes.admin import register_admin_blueprints
        register_admin_blueprints(app)
        registered_blueprints.add('admin')

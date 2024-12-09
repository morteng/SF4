from .admin import register_admin_blueprints

def register_blueprints(app):
    from app.routes.user_routes import user_bp
    from app.routes.public_routes import public_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(public_bp)

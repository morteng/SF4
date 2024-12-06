from flask import Flask
from app.config import config_by_name
from app.extensions import db, login_manager
from app.routes.admin import register_admin_blueprints
from app.routes.visitor_routes import visitor_bp  # Ensure this is imported

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.public_routes import public_routes
    app.register_blueprint(public_routes, url_prefix='/')

    register_admin_blueprints(app)  # Ensure this is called

    app.register_blueprint(visitor_bp, url_prefix='/')  # Register the visitor blueprint

    return app

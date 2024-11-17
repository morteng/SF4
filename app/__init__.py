from flask import Flask
from app.extensions import db

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load appropriate configuration
    if config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from .routes.user_routes import user_bp
    from .routes.admin_routes import admin_bp
    from .routes.bot_routes import bot_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)
    
    return app

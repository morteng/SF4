from flask import Flask
from app.extensions import db, migrate
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.user_routes import user_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.bot_routes import bot_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)

    return app

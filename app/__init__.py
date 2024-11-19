from flask import Flask
from config import get_config
from extensions import init_extensions
from routes import init_routes

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    init_extensions(app)
    init_routes(app)

    # Register public bot blueprint
    from app.routes.public_bot_routes import public_bot_bp
    app.register_blueprint(public_bot_bp)

    # Register public user blueprint
    from app.routes.public_user_routes import public_user_bp
    app.register_blueprint(public_user_bp)

    return app

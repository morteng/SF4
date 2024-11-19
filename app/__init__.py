from flask import Flask
from .config import get_config  # Use relative import
from .extensions import init_extensions  # Use relative import
import routes

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    init_extensions(app)

    # Register public bot blueprint
    from app.routes.public_bot_routes import public_bot_bp
    app.register_blueprint(public_bot_bp)
    print(f"Registered blueprint: {public_bot_bp.name}")

    # Register public user blueprint
    from app.routes.public_user_routes import public_user_bp
    app.register_blueprint(public_user_bp)
    print(f"Registered blueprint: {public_user_bp.name}")

    return app

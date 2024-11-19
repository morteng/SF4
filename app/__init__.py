from flask import Flask, render_template
from app.config import get_config
from app.extensions import init_extensions
from app.routes.admin import admin_bp
from app.routes.user import user_bp
from app.routes.public_bot_routes import public_bot_bp
from app.routes.public_user_routes import public_user_bp

def create_app(config_name='default'):
    config = get_config(config_name)
    app = Flask(__name__)
    app.config.from_object(config)

    init_extensions(app)

    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp)
    app.register_blueprint(public_bot_bp, url_prefix='/bots')
    app.register_blueprint(public_user_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
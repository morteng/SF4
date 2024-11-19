from flask import Flask, render_template
from app.config import get_config
from app.extensions import init_extensions
from app.routes.admin import admin_bp
# from app.routes.user import user_bp  # Commented out or removed

def create_app(config_name='default'):
    config = get_config(config_name)
    app = Flask(__name__)
    app.config.from_object(config)

    init_extensions(app)

    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    # app.register_blueprint(user_bp)  # Commented out or removed

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

from flask import Flask
from .extensions import db, migrate

def create_app(config_name='default'):
    app = Flask(__name__)
    config_class = get_config(config_name)
    if config_class is None:
        raise ValueError(f"Unknown configuration name: {config_name}")
    app.config.from_object(config_class)

    # Initialize extensions and blueprints
    db.init_app(app)
    migrate.init_app(app, db)
    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    return app

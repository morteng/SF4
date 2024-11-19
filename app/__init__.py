from flask import Flask
from config import DefaultConfig, TestingConfig, DevelopmentConfig, ProductionConfig

def create_app(config_name='default'):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config.from_object(TestingConfig)
    elif config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DefaultConfig)

    # Initialize extensions and blueprints
    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    return app

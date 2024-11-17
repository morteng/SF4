from flask import Flask
from app.extensions import db, migrate

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Set appropriate configuration based on config_name
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['DEBUG'] = False
    elif config_name == 'production':
        app.config['DEBUG'] = False
    else:
        app.config['DEBUG'] = True

    # Initialize extensions and register blueprints
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import routes
        from .models import user, stipend, organization, tag, bot, notification

    return app

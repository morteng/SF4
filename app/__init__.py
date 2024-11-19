from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models import init_models
from .routes import init_routes

# Initialize the database and migrate objects
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)

    # Load configuration
    from .config import get_config
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize database and migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize models
    init_models(app)

    # Initialize routes
    init_routes(app)

    return app
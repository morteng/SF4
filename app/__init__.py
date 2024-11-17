from flask import Flask
from config import Config, DevelopmentConfig, TestingConfig, ProductionConfig
from app.extensions import db
import os
from dotenv import load_dotenv

def create_app(config_name=None):
    # Load environment variables from .env file
    load_dotenv()

    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    # Create and configure the app
    app = Flask(__name__)

    # Configure the app based on the selected configuration class
    if config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.admin.bot_routes import admin_bot_bp
    from app.routes.admin.organization_routes import org_bp
    from app.routes.admin.tag_routes import tag_bp
    from app.routes.admin.user_routes import admin_user_bp
    from app.routes.admin.stipend_routes import stipend_bp

    app.register_blueprint(admin_bot_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(admin_user_bp)
    app.register_blueprint(stipend_bp)

    # Initialize the database and create admin user within app context
    with app.app_context():
        db.create_all()  # This replaces init_db()
        
        # Initialize admin user
        from app.models.user import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username=os.environ.get('ADMIN_USERNAME', 'admin'),
                email=os.environ.get('ADMIN_EMAIL', 'admin@example.com'),
                is_admin=True
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin'))
            db.session.add(admin)
            db.session.commit()

    return app

def run_tests():
    """Run tests using pytest with coverage."""
    import pytest
    return pytest.main(['-v', '--cov=app', '--cov-report=term-missing', 'tests/']) == 0

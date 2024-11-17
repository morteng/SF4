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
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin_user')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        
        # Check for existing admin by username OR email
        admin = User.query.filter(
            (User.username == admin_username) | 
            (User.email == admin_email)
        ).first()
        
        if not admin:
            try:
                admin = User(
                    username=admin_username,
                    email=admin_email,
                    is_admin=True
                )
                admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin'))
                db.session.add(admin)
                db.session.commit()
                print(f"Created admin user: {admin_username}")
            except Exception as e:
                print(f"Error creating admin user: {e}")
                db.session.rollback()
        else:
            print(f"Admin user already exists: {admin.username}")

    return app

def run_tests():
    """Run tests using pytest with coverage."""
    import pytest
    return pytest.main(['-v', '--cov=app', '--cov-report=term-missing', 'tests/']) == 0

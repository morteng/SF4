from flask import Flask
from flask_login import LoginManager
from app.extensions import db, migrate  # Ensure db and migrate are imported here
from app.models import Base  # Ensure Base is imported here
from app.routes.admin import admin_bp, bot_bp

login_manager = LoginManager()

def create_app(config_name):
    app = Flask(__name__)
    
    # Load configuration based on environment variable or default to 'development'
    config_module = f"config.{config_name.capitalize()}Config"
    app.config.from_object(config_module)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)  # Initialize Flask-Login

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Register blueprints and other components here if needed
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)  # Register the bot blueprint

    return app

def init_db(app):
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize database: {e}")

def run_migrations():
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Failed to apply migrations: {e}")

def run_tests():
    import pytest
    pytest.main(['-v', 'tests'])

def main():
    app = create_app('development')
    init_db(app)
    run_migrations()
    try:
        app.run()
    except Exception as e:
        print(f"Application failed to start: {e}")

if __name__ == '__main__':
    main()

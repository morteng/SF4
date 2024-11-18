from flask import Flask, jsonify, request, redirect, url_for
from flask_login import LoginManager, login_required
from app.models.user import User  # Import the User model
from app.extensions import db  # Import the db object

def create_app(config_name='default'):
    from app.config import get_config
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'public_user.login'  # Corrected endpoint name

    # Custom unauthorized handler
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/admin/api/'):
            return jsonify({"message": "Unauthorized"}), 401
        else:
            return redirect(url_for('public_user.login'))

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

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

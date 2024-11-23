#app/__init__.py
from flask import Flask
from flask_migrate import Migrate  # Import Flask-Migrate
from app.models.user import User
from app.extensions import db, login_manager, init_extensions 
from werkzeug.security import generate_password_hash
import os

def create_app(config_name='default'):
    from app.config import config_by_name
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    init_extensions(app)
    init_models(app)
    init_routes(app)

    # Initialize the user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    with app.app_context():
        # Check if an admin user exists
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            # Create the default admin user
            username = os.environ.get('ADMIN_USERNAME', 'admin')
            password = os.environ.get('ADMIN_PASSWORD', 'password')
            email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created.")

    return app

def init_models(app):
    with app.app_context():
        from app.models import association_tables
        from app.models.bot import Bot
        from app.models.notification import Notification
        from app.models.organization import Organization
        from app.models.stipend import Stipend
        from app.models.tag import Tag
        from app.models.user import User

def init_routes(app):
    from app.routes import routes_bp
    app.register_blueprint(routes_bp)

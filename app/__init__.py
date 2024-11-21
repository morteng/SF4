from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os  # Import the os module

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(Config)

    init_extensions(app)
    init_routes(app)
    
    with app.app_context():
        init_admin_user(app)

    return app

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'visitor.login'

def init_routes(app):
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.visitor_routes import visitor_bp  # Ensure this matches the file name

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(visitor_bp)  # No prefix for visitor routes

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

def init_admin_user(app):
    from app.models.user import User
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')
    admin_email = os.getenv('ADMIN_EMAIL')

    if not User.query.filter_by(username=admin_username).first():
        admin_user = User(
            username=admin_username,
            email=admin_email,
            is_admin=True
        )
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()

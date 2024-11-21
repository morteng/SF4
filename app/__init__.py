from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(Config)

    init_extensions(app)
    init_routes(app)

    return app

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'visitor.login'

def init_routes(app):
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.visitor import visitor_bp

    app.register_blueprint(admin_bp, url_prefix='/admin/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(visitor_bp)

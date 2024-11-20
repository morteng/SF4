import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    init_extensions(app)
    init_models(app)
    init_routes(app)

    return app

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'  # Set the login view for Flask-Login

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
    with app.app_context():
        from app.routes.public_user_routes import public_user_bp
        from app.routes.admin.bot_routes import admin_bot_bp
        from app.routes.admin.organization_routes import org_bp
        from app.routes.admin.stipend_routes import admin_stipend_bp
        from app.routes.admin.tag_routes import tag_bp
        from app.routes.admin.user_routes import user_bp

        app.register_blueprint(public_user_bp)
        app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
        app.register_blueprint(org_bp, url_prefix='/admin/organizations')
        app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
        app.register_blueprint(tag_bp, url_prefix='/admin/tags')
        app.register_blueprint(user_bp, url_prefix='/user')

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

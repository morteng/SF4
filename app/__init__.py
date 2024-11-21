# app/__init__.py
from flask import Flask
from app.models.user import User
from app.extensions import db, login_manager

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

    return app

def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)

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
    from app.routes import visitor_bp, admin_bot_bp, admin_org_bp, admin_stipend_bp, admin_tag_bp, admin_user_bp, user_bp
    app.register_blueprint(visitor_bp)
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(admin_user_bp, url_prefix='/admin/users')
    app.register_blueprint(user_bp, url_prefix='/user')
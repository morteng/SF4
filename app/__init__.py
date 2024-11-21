from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration based on the environment
    if config_name == 'development':
        app.config.from_object('app.config.DevelopmentConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    elif config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    else:
        app.config.from_object('app.config.DefaultConfig')

    # Initialize extensions
    init_extensions(app)
    
    # Initialize models
    init_models(app)
    
    # Initialize routes
    init_routes(app)

    return app

def init_extensions(app):
    db.init_app(app)  # Ensure SQLAlchemy is initialized with the app

def init_models(app):
    from app.models import User, Stipend, Tag, Organization, Bot, Notification
    with app.app_context():
        db.create_all()

def init_routes(app):
    from app.routes.visitor_routes import visitor_bp
    from app.routes.admin.bot_routes import admin_bot_bp
    from app.routes.admin.organization_routes import org_bp
    from app.routes.admin.stipend_routes import admin_stipend_bp
    from app.routes.admin.tag_routes import tag_bp
    from app.routes.admin.user_routes import user_bp
    from app.routes.user_routes import user_bp as user_profile_bp

    app.register_blueprint(visitor_bp)
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(tag_bp, url_prefix='/admin/tags')
    app.register_blueprint(user_bp, url_prefix='/admin/users')
    app.register_blueprint(user_profile_bp, url_prefix='/user')

from flask import Flask
from app.extensions import db
from app.config import config_by_name
# Importing admin blueprints
from app.routes.admin.bot_routes import admin_bot_bp
from app.routes.admin.organization_routes import org_bp
from app.routes.admin.stipend_routes import admin_stipend_bp
from app.routes.admin.tag_routes import tag_bp
# Importing user and visitor blueprints
from app.routes.user_routes import user_bp
from app.routes.visitor_routes import visitor_bp

# Importing all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.bot import Bot
from app.models.organization import Organization
from app.models.stipend import Stipend
from app.models.notification import Notification
from app.models.tag import Tag
from app.models.association_tables import user_organization, bot_tag

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    
    # Registering admin blueprints
    app.register_blueprint(admin_bot_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(admin_stipend_bp)
    app.register_blueprint(tag_bp)
    
    # Registering user and visitor blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(visitor_bp)
    
    return app

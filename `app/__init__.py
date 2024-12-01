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
from app.routes.visitor_routes import visitor_bp  # Ensure correct import

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    
    # Registering admin blueprints
    app.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
    app.register_blueprint(org_bp, url_prefix='/admin/organizations')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
    app.register_blueprint(tag_bp, url_prefix='/admin/tags')
    
    # Registering user and visitor blueprints
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(visitor_bp)  # Adjust prefix if necessary
    
    return app

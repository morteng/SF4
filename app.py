import os
from flask import Flask, flash, redirect, url_for, render_template
from flask_login import LoginManager
from app.routes.visitor_routes import visitor_bp
from app.models.user import User
from app import create_app

def create_app(config_name='development'):
    app = Flask(__name__, template_folder=os.path.abspath('app/templates'))
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'visitor.login'
    
    # Register blueprints
    from app.routes.visitor_routes import visitor_bp
    from app.routes.admin.bot_routes import admin_bot_bp
    from app.routes.admin.organization_routes import org_bp
    from app.routes.admin.stipend_routes import admin_stipend_bp  # Updated import
    from app.routes.admin.tag_routes import tag_bp
    from app.routes.admin.user_routes import user_bp
    app.register_blueprint(visitor_bp)
    app.register_blueprint(admin_bot_bp, url_prefix='/admin')
    app.register_blueprint(org_bp, url_prefix='/admin')
    app.register_blueprint(admin_stipend_bp, url_prefix='/admin')  # Updated registration
    app.register_blueprint(tag_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/admin')
    
    # Other setup code...
    
    return app

if __name__ == '__main__':
    app = create_app()
    print(f"Serving templates from: {app.template_folder}")
    app.run(debug=True)

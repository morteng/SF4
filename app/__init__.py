from flask import Flask
from .routes import public_user_routes, public_bot_routes
from .routes.admin import bot_routes, organization_routes, stipend_routes, tag_routes, user_routes

def create_app(config_name='default'):
    app = Flask(__name__)

    # Configuration and initialization...
    # (Assuming you have some configuration setup here)

    def register_blueprints(app):
        # Register public blueprints
        app.register_blueprint(public_user_routes.bp)
        app.register_blueprint(public_bot_routes.bp)

        # Register admin blueprints
        app.register_blueprint(bot_routes.bot_bp)
        app.register_blueprint(organization_routes.organization_bp)
        app.register_blueprint(stipend_routes.stipend_bp)
        app.register_blueprint(tag_routes.tag_bp)
        app.register_blueprint(user_routes.user_bp)

    register_blueprints(app)

    return app

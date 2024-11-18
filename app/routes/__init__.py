from flask import Blueprint

# Create a blueprint for the main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "Welcome to the Stipend Discovery Website!"

@main_bp.route('/about')
def about():
    return "This is the about page."

def register_routes(app):
    # Register the main blueprint
    app.register_blueprint(main_bp)

    # Import and register other blueprints here if needed
    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from .user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

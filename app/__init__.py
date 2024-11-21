from flask import Flask
from config import Config
from app.extensions import init_extensions, init_admin_user

def create_app(config_name='default'):
    # Initialize the Flask application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize extensions and routes
    init_extensions(app)
    init_routes(app)

    # Ensure the database file exists
    from app.extensions import db
    with app.app_context():
        db_file_path = os.path.join(app.instance_path, 'site.db')
        if not os.path.exists(db_file_path):
            print(f"Database file does not exist. Creating it now...")  # Debugging line
            db.create_all()

    return app

def init_routes(app):
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

# Other initialization functions can be added here

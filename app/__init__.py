import os
from flask import Flask
from config import Config
from app.extensions import init_extensions, init_admin_user, db

def create_app(config_name='default'):
    # Initialize the Flask application with instance_relative_config=True
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Print the current working directory for debugging
    print(f"Current Working Directory: {os.getcwd()}")  # Debugging line

    # Ensure the instance/ directory exists
    instance_path = app.instance_path
    if not os.path.exists(instance_path):
        print(f"Creating directory: {instance_path}")  # Debugging line
        os.makedirs(instance_path)
    else:
        print(f"Directory already exists: {instance_path}")  # Debugging line

    # Print the database URI for debugging
    print(f"Database URI from config: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debugging line

    # Check if the instance/ directory is writable
    if not os.access(instance_path, os.W_OK):
        print(f"Directory {instance_path} is not writable.")  # Debugging line
    else:
        print(f"Directory {instance_path} is writable.")  # Debugging line

        # Test creating a file in the instance directory
        test_file_path = os.path.join(instance_path, 'test.txt')
        try:
            with open(test_file_path, 'w') as f:
                f.write("Test file")
            print(f"Successfully created and wrote to {test_file_path}")
        except Exception as e:
            print(f"Failed to create or write to {test_file_path}: {e}")

    # Manually check if we can create a SQLite database file
    db_file_path = os.path.join(instance_path, 'site.db')
    try:
        import sqlite3
        conn = sqlite3.connect(db_file_path)
        print(f"Successfully created and connected to the database at {db_file_path}")
        conn.close()
    except Exception as e:
        print(f"Failed to create or connect to the database at {db_file_path}: {e}")

    # Initialize extensions
    init_extensions(app)

    # Ensure the database file exists and create it if necessary
    db_file_path = os.path.join(instance_path, 'site.db')
    print(f"Database file path: {db_file_path}")  # Debugging line

    try:
        if not os.path.exists(db_file_path):
            print(f"Database file does not exist. Creating it now...")  # Debugging line
            with app.app_context():
                db.create_all()
        else:
            print(f"Database file already exists.")  # Debugging line
    except Exception as e:
        print(f"An error occurred while creating the database: {e}")  # Debugging line

    # Initialize routes
    init_routes(app)

    return app

def init_routes(app):
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

# Other initialization functions can be added here

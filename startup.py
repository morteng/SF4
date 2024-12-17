# startup.py

import os
from app import create_app, db
from app.utils import init_admin_user
from dotenv import load_dotenv

def initialize_database():
    # Load environment variables
    load_dotenv()

    # Create the Flask application with the specified configuration
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))

    # Initialize database and migrate
    with app.app_context():
        db.create_all()  # Creates all tables if they don't exist

        # Initialize admin user
        init_admin_user()

if __name__ == '__main__':
    initialize_database()

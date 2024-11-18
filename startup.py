import os
import pytest
from app import create_app, db  # Import the existing db instance
from dotenv import load_dotenv  # Ensure .env file is loaded

# Load environment variables from .env file
load_dotenv()

def init_db(app):
    with app.app_context():
        print(f"Initializing database with URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        db.create_all()
        print("Database initialization complete.")

def run_tests():
    result = pytest.main(['-v', 'tests/'])
    if result != 0:
        print("Tests failed. Aborting startup.")
        exit(1)
    else:
        print("All tests passed successfully.")

def main():
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app = create_app(config_name)
    
    # Print the configuration class being used
    print(f"Using configuration: {app.config['ENV']}")
    print(f"Loaded configuration: {app.config}")

    # Initialize the database
    init_db(app)

    # Run tests
    run_tests()

    # Run the application
    app.run()

if __name__ == '__main__':
    main()

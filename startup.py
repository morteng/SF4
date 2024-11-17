import sys
import os
from dotenv import load_dotenv
from flask_migrate import upgrade as migrate_upgrade
from app import create_app, db

def run_migrations(app):
    with app.app_context():
        migrate_upgrade()

def run_tests():
    import pytest
    pytest.main(['-v', '--cov=app', '--cov-report=term'])

def main():
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Get config from environment
        config_name = os.getenv('FLASK_CONFIG', 'development')
        
        print("Current Python Path:", sys.path)
        print(f"Attempting to create app with config: '{config_name}'")
        
        app = create_app(config_name)
        print(f"App created successfully with config: {config_name}")
        
        # Use a single app context for all database operations
        with app.app_context():
            print("Initializing db")
            db.create_all()
        
            print("Running migrations...")
            run_migrations(app)
            
            print("Migrations completed successfully.")
        
            print("Running tests...")
            run_tests()
            
            print("Tests completed successfully.")
            
            print("Starting the app...")
            app.run(debug=True)
            
    except Exception as e:
        print(f"Error during startup: {e}")

if __name__ == '__main__':
    main()

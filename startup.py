import sys
from flask_migrate import upgrade as migrate_upgrade
from app import create_app, db

def run_migrations(app):
    # Remove the with context here since we'll use the outer context
    migrate_upgrade()

def run_tests():
    import pytest
    pytest.main(['-v', '--cov=app', '--cov-report=term'])

def main():
    try:
        print("Current Python Path:", sys.path)
        print("Attempting to create app with config: 'development'")
        app = create_app('development')
        print(f"App created successfully with config: development")
        
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

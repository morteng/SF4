import sys
from flask_migrate import upgrade as migrate_upgrade
from app import create_app, db

def run_migrations(app, migrate):
    with app.app_context():
        migrate.init_app(app, db)  # Initialize Migrate with app and db
        migrate_upgrade()

def run_tests():
    import pytest
    pytest.main(['-v', '--cov=app', '--cov-report=html'])

def main():
    try:
        print("Current Python Path:", sys.path)
        print("Attempting to create app with config: 'development'")
        app, migrate = create_app('development')
        print(f"App created successfully with config: development")
        
        print("Initializing db")
        with app.app_context():
            db.create_all()
        
        print("Running migrations...")
        run_migrations(app, migrate)
        
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

from flask_migrate import Migrate, upgrade as migrate_upgrade
from app import create_app, db

def run_migrations():
    app = create_app('development')
    with app.app_context():
        migrate = Migrate(app, db)
        migrate_upgrade()

def run_tests():
    import pytest
    pytest.main(['-v', '--cov=app', '--cov-report=html'])

def main():
    try:
        print("Attempting to create app with config: 'development'")
        app = create_app('development')
        print(f"Creating app with config: {app.config['ENV']}")
        
        print("Initializing db")
        with app.app_context():
            db.create_all()
        
        print("Initializing migrate")
        run_migrations()
        
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

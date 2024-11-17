import sys
from flask_migrate import upgrade as migrate_upgrade
from app import create_app, db

def run_migrations():
    # Don't pass app since we'll use current_app
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
        
        # Create a single app context for all operations
        ctx = app.app_context()
        ctx.push()
        
        try:
            print("Initializing db")
            db.create_all()
        
            print("Running migrations...")
            run_migrations()
            
            print("Migrations completed successfully.")
            
            # Pop context before running tests
            ctx.pop()
            
            print("Running tests...")
            run_tests()
            
            print("Tests completed successfully.")
            
            print("Starting the app...")
            app.run(debug=True)
            
        except Exception as e:
            # Ensure context is popped even if there's an error
            if ctx:
                ctx.pop()
            raise e
            
    except Exception as e:
        print(f"Error during startup: {e}")

if __name__ == '__main__':
    main()

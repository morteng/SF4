import sys
import os
import signal
from dotenv import load_dotenv
from flask_migrate import upgrade as migrate_upgrade
from app import create_app, db

def signal_handler(signum, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

def run_migrations():
    # Remove app context parameter since we'll use the outer context
    migrate_upgrade()

def run_tests():
    import pytest
    pytest.main(['-x', '--cov=app', '--cov-report=term'])

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
        
        # Create a single app context for the setup phase
        with app.app_context():
            print("Initializing db")
            db.create_all()
        
            print("Running migrations...")
            run_migrations()
            print("Migrations completed successfully.")
        
            print("Running tests...")
            run_tests()
            print("Tests completed successfully.")
        
        # Run the app outside of the setup context
        print("Starting the app...")
        app.run(debug=True)
            
    except Exception as e:
        print(f"Error during startup: {e}")
        sys.exit(1)  # Exit with error code

if __name__ == '__main__':
    main()

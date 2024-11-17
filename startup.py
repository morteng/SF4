import sys
import subprocess
from app import create_app
from app.extensions import db

def run_migrations():
    """Run database migrations."""
    try:
        subprocess.run(['alembic', 'upgrade', 'head'], check=True)
        print("Migrations completed successfully.")
    except subprocess.CalledProcessError:
        print("Error running migrations.")
        sys.exit(1)

def run_tests():
    """Run pytest and check test coverage."""
    try:
        result = subprocess.run(['pytest', '--cov=app', '--cov-report=term-missing'], capture_output=True, text=True)
        print(result.stdout)
        
        # Check if tests passed
        if result.returncode != 0:
            print("Tests failed:")
            print(result.stderr)
            sys.exit(1)
        
        print("All tests passed successfully.")
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

def main():
    print(f"Attempting to create app with config: 'default'")  # Add this line
    # Create the application instance
    app = create_app('default')

    # Run migrations and initialize admin user
    try:
        with app.app_context():
            # Run migrations (replaces db.create_all())
            run_migrations()

            # Initialize the admin user after migrations
            from app.utils import init_admin_user
            init_admin_user()
    except Exception as e:
        print(f"Error during startup: {e}")
        sys.exit(1)

    # Run tests
    run_tests()

    # If we get here, tests passed - run the app
    app.run(debug=True)

if __name__ == '__main__':
    main()

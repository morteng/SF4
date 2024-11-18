import os
import pytest
from app import create_app, db  # Import the existing db instance

# Initialize the database
def init_db(app):
    with app.app_context():
        db.create_all()

# Run tests
def run_tests():
    result = pytest.main(['-v', 'tests/'])
    if result != 0:
        print("Tests failed. Aborting startup.")
        exit(1)

def main():
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app = create_app(config_name)

    # Initialize the database
    init_db(app)

    # Run tests
    run_tests()

    # Run the application
    app.run()

if __name__ == '__main__':
    main()

import os
import pytest
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from app.config import get_config  # Corrected import statement

# Initialize the database
def init_db(app):
    db = SQLAlchemy(app)
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
    config = get_config(config_name)
    app = create_app(config)

    # Initialize the database
    init_db(app)

    # Run tests
    run_tests()

    # Run the application
    app.run()

if __name__ == '__main__':
    main()

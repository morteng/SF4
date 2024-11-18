import os
from app import create_app
from app.config import get_config  # Corrected import statement

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

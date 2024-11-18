from dotenv import load_dotenv
import os
from app import create_app, db

def init_db(app):
    with app.app_context():
        db.create_all()

def run_migrations():
    # Run migrations if needed
    pass

def run_tests():
    # Run tests if needed
    pass

def main():
    load_dotenv()  # Load environment variables from .env file
    config_name = os.getenv('FLASK_CONFIG', 'default')
    app = create_app(config_name)
    init_db(app)
    run_migrations()
    run_tests()
    app.run(debug=True)

if __name__ == '__main__':
    main()

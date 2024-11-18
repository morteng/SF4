from app import create_app, db
import os

def init_db():
    """Initialize the database by creating all tables."""
    app = create_app()
    with app.app_context():
        print("Initializing database...")
        db.create_all()

def run_migrations():
    """Run database migrations."""
    from flask_migrate import upgrade
    app = create_app()
    with app.app_context():
        print("Running migrations...")
        upgrade()

def run_tests():
    """Run tests using pytest."""
    import pytest
    exit_code = pytest.main(['tests'])
    if exit_code != 0:
        print("Tests failed. Aborting startup.")
        os._exit(exit_code)

def main():
    init_db()
    run_migrations()
    run_tests()
    app = create_app()
    app.run()

if __name__ == '__main__':
    main()

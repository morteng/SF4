import os
from app import create_app, db
from config import get_config

def init_db(app):
    with app.app_context():
        db.create_all()

def run_migrations():
    from alembic.config import Config as AlembicConfig
    from alembic import command
    alembic_cfg = AlembicConfig("migrations/alembic.ini")
    command.upgrade(alembic_cfg, "head")

def run_tests():
    import pytest
    result = pytest.main(['-v', 'tests'])
    return result == 0

def main():
    config_name = os.getenv('FLASK_CONFIG', 'default')
    config = get_config(config_name)
    
    app = create_app(config_name=config_name)
    with app.app_context():
        init_db(app)
        run_migrations()
        if not run_tests():
            print("Tests failed. Aborting startup.")
            return
        # Run the application
        app.run()

if __name__ == '__main__':
    main()

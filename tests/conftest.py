import pytest
from app import create_app, db
from alembic.config import Config
from alembic import command

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        # Run migrations
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        db.session.commit()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

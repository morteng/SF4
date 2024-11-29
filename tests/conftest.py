import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        _db.session = _db.create_scoped_session(options={"bind": connection})
        yield _db
        _db.session.remove()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope='function')
def client(app, db):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module', autouse=True)
def init_admin_user(db):
    admin_user = db.session.query(User).filter_by(email='admin@example.com').first()
    if not admin_user:
        admin_user = User(
            username='admin_user',
            password_hash='pbkdf2:sha256:150000$XbL3IjWn$3d8Kq7J29e4gFyhiuQlZIl12tXcVU8S2R5Qx5hPZV0k=',
            email='admin@example.com',
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

import pytest
from app import create_app
from app.extensions import _db
from app.models.user import User

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        # Initialize admin user
        admin_user = _db.session.query(User).filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User(
                username='admin_user',
                password_hash='pbkdf2:sha256:150000$XbL3IjWn$3d8Kq7J29e4gFyhiuQlZIl12tXcVU8S2R5Qx5hPZV0k=',
                email='admin@example.com',
                is_admin=True
            )
            _db.session.add(admin_user)
            _db.session.commit()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        _db.session.bind = connection
        yield _db.session
        transaction.rollback()
        connection.close()

@pytest.fixture(scope='function')
def client(app, db):
    with app.test_client() as client:
        yield client

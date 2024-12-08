import pytest
from app import create_app, db
from app.models.user import User
from sqlalchemy.orm import scoped_session, sessionmaker  # Import scoped_session and sessionmaker

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(db_session):
    user = User(username='admin', email='admin@example.com', is_admin=True)
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope='function')
def db_session(app, db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection)
    Session = scoped_session(sessionmaker(bind=db.engine))
    session = Session()

    yield session

    # Rollback the transaction and close the session after each test
    session.rollback()
    connection.close()
    session.remove()  # Use session.remove() instead of session.close()

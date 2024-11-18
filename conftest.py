import pytest
from app import create_app, db, run_migrations  # Import the run_migrations function

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        run_migrations()  # Run migrations before tests
        yield app.test_client()
        db.session.remove()
        db.drop_all()

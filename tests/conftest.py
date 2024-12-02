import pytest  # Add this import statement

@pytest.fixture
def db(_db):
    return _db

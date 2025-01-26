import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import StaleDataError
from tests.utils import extract_csrf_token

@pytest.fixture
def logged_in_admin():
    # Implementation of logged_in_admin fixture
    pass

FREEZEGUN_INSTALLED = True

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import StaleDataError
from tests.base_test_case import BaseTestCase

@pytest.fixture
def logged_in_admin():
    # Implementation of logged_in_admin fixture
    pass

def extract_csrf_token(response_data):
    # Implementation of extract_csrf_token function
    pass

class BaseCRUDTest(BaseTestCase):
    # Implementation of BaseCRUDTest class
    pass

FREEZEGUN_INSTALLED = True

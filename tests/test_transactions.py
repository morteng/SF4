from app import db
from app.models import Stipend
from tests.base_test_case import BaseTestCase

class TestTransactions(BaseTestCase):
    def test_rollback_on_error(self):
        initial_count = Stipend.query.count()
        
        try:
            with db.session.begin_nested():
                stipend = Stipend(name="Test Rollback")
                db.session.add(stipend)
                raise ValueError("Simulated error")
        except ValueError:
            pass
            
        self.assertEqual(Stipend.query.count(), initial_count)

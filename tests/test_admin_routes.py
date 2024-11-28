import unittest
from app import create_app, db
from app.models import User, Stipend
from flask_login import login_user

class AdminRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_admin_access(self):
        user = User(username='testuser', is_admin=True)
        db.session.add(user)
        db.session.commit()
        with self.app.test_client() as client:
            login_user(user)
            response = client.get('/admin/stipends/')
            self.assertEqual(response.status_code, 200)

    def test_non_admin_access(self):
        user = User(username='testuser', is_admin=False)
        db.session.add(user)
        db.session.commit()
        with self.app.test_client() as client:
            login_user(user)
            response = client.get('/admin/stipends/')
            self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()

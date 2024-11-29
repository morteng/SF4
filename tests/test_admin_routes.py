import unittest
from app import create_app, db
from app.models import User
from flask_login import login_user
from werkzeug.security import generate_password_hash

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

    def create_user(self, username='testuser', password='testpassword', email='testuser@example.com', is_admin=False):
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def test_admin_access(self):
        user = self.create_user(is_admin=True)
        with self.app.test_request_context():
            login_user(user)
            with self.app.test_client() as client:
                response = client.get('/admin/stipends/')
                self.assertEqual(response.status_code, 200)

    def test_non_admin_access(self):
        user = self.create_user(is_admin=False)
        with self.app.test_request_context():
            login_user(user)
            with self.app.test_client() as client:
                response = client.get('/admin/stipends/')
                self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()

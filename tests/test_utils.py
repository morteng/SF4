# tests/test_utils.py

import os
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
from app.utils import admin_required, init_admin_user
from app.models.user import User
from app.extensions import db

class TestAdminRequiredDecorator:
    def setup_method(self):
        self.app = create_test_app()
        with self.app.app_context():
            db.create_all()

    def teardown_method(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch('app.utils.current_user')
    @patch('flask.abort', side_effect=MagicMock())
    def test_admin_required_with_non_authenticated_user(self, mock_abort, mock_current_user, app):
        mock_current_user.is_authenticated = False
        mock_current_user.is_admin = False

        @admin_required
        def test_function():
            return "Success"

        with app.test_request_context('/'):
            response = test_function()
            mock_abort.assert_called_with(403)

    @patch('app.utils.current_user')
    @patch('flask.abort', side_effect=MagicMock())
    def test_admin_required_with_non_admin_user(self, mock_abort, mock_current_user, app):
        mock_current_user.is_authenticated = True
        mock_current_user.is_admin = False

        @admin_required
        def test_function():
            return "Success"

        with app.test_request_context('/'):
            response = test_function()
            mock_abort.assert_called_with(403)

    @patch('app.utils.current_user')
    def test_admin_required_with_admin_user(self, mock_current_user, app):
        mock_current_user.is_authenticated = True
        mock_current_user.is_admin = True

        @admin_required
        def test_function():
            return "Success"

        with app.test_request_context('/'):
            response = test_function()
            assert response == "Success"

class TestInitAdminUser:
    def setup_method(self):
        self.app = create_test_app()
        with self.app.app_context():
            db.create_all()

    def teardown_method(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch.dict(os.environ, {'ADMIN_USERNAME': 'admin', 'ADMIN_PASSWORD': 'password123', 'ADMIN_EMAIL': 'admin@example.com'})
    def test_init_admin_user_creates_new_admin(self, app, db_session):
        with app.app_context():
            init_admin_user()
            admin = User.query.filter_by(username='admin').first()
            assert admin is not None
            assert admin.username == 'admin'
            assert admin.email == 'admin@example.com'
            assert admin.is_admin

    @patch.dict(os.environ, {'ADMIN_USERNAME': 'admin', 'ADMIN_PASSWORD': 'password123', 'ADMIN_EMAIL': 'admin@example.com'})
    def test_init_admin_user_does_not_create_duplicate(self, app, db_session):
        with app.app_context():
            init_admin_user()
            init_admin_user()  # Call it again to ensure no duplicates
            admins = User.query.filter_by(username='admin').all()
            assert len(admins) == 1

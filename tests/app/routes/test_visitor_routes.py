import pytest
from flask import url_for
from app.models.user import User

@pytest.mark.usefixtures("db")
class TestVisitorRoutes:

    def test_login_redirects_admin_to_admin_interface(self, admin_auth_client):
        response = admin_auth_client.get(url_for('visitor.login'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin Stipend Index' in response.data

    def test_login_redirects_user_to_profile(self, auth_client):
        response = auth_client.get(url_for('visitor.login'), follow_redirects=True)
        assert response.status_code == 200
        assert b'User Profile' in response.data

# tests/app/routes/admin/test_stipend_errors.py
import pytest
from flask import url_for
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm
from datetime import datetime, timedelta
from tests.conftest import logged_in_admin, db_session, test_stipend, stipend_data

def test_create_stipend_with_none_result(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_create_stipend(*args, **kwargs):
            return None

        monkeypatch.setattr('app.services.stipend_service.create_stipend', mock_create_stipend)

        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data)
        
        assert response.status_code == 200
        assert b"Stipend creation failed due to invalid input." in response.data  # Confirm error message is present

        stipends = db_session.query(Stipend).filter_by(name=stipend_data['name']).all()
        assert len(stipends) == 0  # Ensure no stipend was created

from flask import url_for
from app.models.stipend import Stipend
from tests.conftest import logged_in_admin, stipend_data, db_session
import pytest
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR

def test_create_stipend_with_none_result(stipend_data, logged_in_admin, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        def mock_create_stipend(*args, **kwargs):
            return None

        monkeypatch.setattr('app.services.stipend_service.create_stipend', mock_create_stipend)
    
        stipend_data['submit'] = 'Submit'  # Add the submit field to stipend_data
    
        response = logged_in_admin.post(url_for('admin.stipend.create'), data=stipend_data, follow_redirects=True)
    
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_STIPEND_ERROR"].encode() in response.data
        assert b'Create Stipend' in response.data
        assert b'<input name="name"' in response.data
    
        stipends = db_session.query(Stipend).filter_by(name=stipend_data['name']).all()
        assert len(stipends) == 0

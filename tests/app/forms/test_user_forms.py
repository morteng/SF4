# tests/app/forms/test_user_forms.py



import pytest
from app.forms.admin_forms import UserForm
from wtforms.validators import ValidationError


def test_user_form_validate():
    form = UserForm(original_username='test_user', original_email='test@example.com')
    form.username.data = 'new_test_user'
    form.email.data = 'new_test@example.com'
    assert form.validate() is True

def test_user_form_validate_same_username_and_email():
    form = UserForm(original_username='test_user', original_email='test@example.com')
    form.username.data = 'test_user'
    form.email.data = 'test@example.com'
    assert form.validate() is True



def test_user_form_validate_existing_username(monkeypatch):
    def mock_query_filter_by(*args, **kwargs):
        class MockQuery:
            def first(self):
                return True
        return MockQuery()
    monkeypatch.setattr('app.forms.admin_forms.User.query', mock_query_filter_by)
    form = UserForm(original_username='test_user', original_email='test@example.com')
    form.username.data = 'existing_user'
    form.email.data = 'new_test@example.com'
    with pytest.raises(ValidationError):
        form.validate_username(form.username)

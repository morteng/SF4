import pytest
from app.forms.admin_forms import StipendForm
from app.constants import FlashMessages

def test_stipend_form_validation():
    """Test validation of the StipendForm."""
    form = StipendForm()

    # Test valid date/time
    form.application_deadline.data = "2023-10-31 23:59:59"
    assert form.validate()

    # Test invalid date/time
    form.application_deadline.data = "invalid-date"
    assert not form.validate()
    assert FlashMessages.INVALID_DATE_FORMAT in form.application_deadline.errors

    # Test missing required field
    form.application_deadline.data = None
    assert not form.validate()
    assert FlashMessages.MISSING_FIELD_ERROR in form.application_deadline.errors

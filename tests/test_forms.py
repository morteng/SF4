from app.forms.admin_forms import StipendForm
from freezegun import freeze_time

def test_stipend_form_validation():
    """Test validation of the StipendForm."""
    form = StipendForm()

    # Test valid date/time
    with freeze_time("2023-10-01 12:00:00"):
        form.application_deadline.data = "2023-10-31 23:59:59"
        assert form.validate()

    # Test invalid date/time
    form.application_deadline.data = "invalid-date"
    assert not form.validate()

    # Test missing required field
    form.application_deadline.data = None
        assert not form.validate()

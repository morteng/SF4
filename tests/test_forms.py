from app.constants import FlashMessages
from app.forms.admin_forms import StipendForm

def test_custom_date_time_field_leap_year():
    form = StipendForm()
    form.application_deadline.data = "2023-02-29 12:00:00"  # Invalid leap year
    assert not form.validate()
    assert FlashMessages.INVALID_LEAP_YEAR_ERROR in form.application_deadline.errors

def test_custom_date_time_field_invalid_time():
    form = StipendForm()
    form.application_deadline.data = "2023-01-01 25:00:00"  # Invalid time
    assert not form.validate()
    assert FlashMessages.DATE_FORMAT_ERROR in form.application_deadline.errors

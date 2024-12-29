import pytest
from freezegun import freeze_time
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

@pytest.mark.parametrize("date_str,expected_error", [
    ("2023-02-29", FlashMessages.INVALID_LEAP_YEAR_DATE),  # Invalid leap year
    ("2023-13-01", FlashMessages.INVALID_DATE_FORMAT), # Invalid month
    ("2023-00-01", FlashMessages.INVALID_DATE_FORMAT), # Invalid month
    ("2023-01-32", FlashMessages.INVALID_DATE_FORMAT), # Invalid day
    ("", FlashMessages.MISSING_DATE_FIELD),           # Missing date
    ("2023/01/01", FlashMessages.INVALID_DATE_FORMAT),# Wrong format
])
def test_date_validation(date_str, expected_error):
    form = StipendForm()
    form.application_deadline.data = f"{date_str} 12:00:00"
    assert not form.validate()
    assert expected_error in form.application_deadline.errors

@pytest.mark.parametrize("time_str,expected_error", [
    ("25:00:00", FlashMessages.INVALID_TIME_RANGE),  # Invalid hour
    ("12:60:00", FlashMessages.INVALID_TIME_RANGE),  # Invalid minute
    ("12:00:60", FlashMessages.INVALID_TIME_RANGE),  # Invalid second
    ("", FlashMessages.MISSING_TIME_FIELD),          # Missing time
    ("12-00-00", FlashMessages.INVALID_TIME_FORMAT), # Wrong format
])
def test_time_validation(time_str, expected_error):
    form = StipendForm()
    form.application_deadline.data = f"2023-01-01 {time_str}"
    assert not form.validate()
    assert expected_error in form.application_deadline.errors
from app.constants import FlashMessages
from app.forms.admin_forms import StipendForm

def test_custom_date_time_field_leap_year():
    form = StipendForm()
    form.application_deadline.data = "2023-02-29 12:00:00"  # Invalid leap year
    assert not form.validate()
    assert FlashMessages.INVALID_LEAP_YEAR_DATE in form.application_deadline.errors

def test_custom_date_time_field_invalid_time():
    form = StipendForm()
    form.application_deadline.data = "2023-01-01 25:00:00"  # Invalid time
    assert not form.validate()
    assert FlashMessages.INVALID_TIME_COMPONENTS in form.application_deadline.errors
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
from app.constants import FlashMessages
from app.forms.admin_forms import StipendForm

def test_custom_date_time_field_leap_year():
    form = StipendForm()
    form.application_deadline.data = "2023-02-29 12:00:00"  # Invalid leap year
    assert not form.validate()
    assert FlashMessages.INVALID_LEAP_YEAR_DATE in form.application_deadline.errors

def test_custom_date_time_field_invalid_time():
    form = StipendForm()
    form.application_deadline.data = "2023-01-01 25:00:00"  # Invalid time
    assert not form.validate()
    assert FlashMessages.INVALID_TIME_COMPONENTS in form.application_deadline.errors

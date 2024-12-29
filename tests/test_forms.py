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
import pytest
from freezegun import freeze_time
from app.forms.admin_forms import StipendForm

def test_valid_date_time():
    """Test valid date/time format"""
    form = StipendForm(application_deadline="2023-10-31 23:59:59")
    assert form.validate() is True

def test_invalid_date_time():
    """Test invalid date/time format"""
    form = StipendForm(application_deadline="2023-02-30 25:00:00")
    assert form.validate() is False
import pytest
from freezegun import freeze_time
from app.forms import StipendForm
from app.constants import (
    INVALID_DATE_FORMAT,
    INVALID_TIME_FORMAT,
    INVALID_LEAP_YEAR,
    INVALID_TIME_RANGE,
    MISSING_DATE_FIELD,
    MISSING_TIME_FIELD
)

@pytest.mark.parametrize("date_str,expected_error", [
    ("2023-02-29", INVALID_LEAP_YEAR),  # Invalid leap year
    ("2023-13-01", INVALID_DATE_FORMAT), # Invalid month
    ("2023-00-01", INVALID_DATE_FORMAT), # Invalid month
    ("2023-01-32", INVALID_DATE_FORMAT), # Invalid day
    ("", MISSING_DATE_FIELD),           # Missing date
    ("2023/01/01", INVALID_DATE_FORMAT),# Wrong format
])
def test_date_validation(date_str, expected_error):
    form = StipendForm()
    form.application_deadline.data = f"{date_str} 12:00:00"
    assert not form.validate()
    assert expected_error in form.application_deadline.errors

@pytest.mark.parametrize("time_str,expected_error", [
    ("25:00:00", INVALID_TIME_RANGE),  # Invalid hour
    ("12:60:00", INVALID_TIME_RANGE),  # Invalid minute
    ("12:00:60", INVALID_TIME_RANGE),  # Invalid second
    ("", MISSING_TIME_FIELD),          # Missing time
    ("12-00-00", INVALID_TIME_FORMAT), # Wrong format
])
def test_time_validation(time_str, expected_error):
    form = StipendForm()
    form.application_deadline.data = f"2023-01-01 {time_str}"
    assert not form.validate()
    assert expected_error in form.application_deadline.errors

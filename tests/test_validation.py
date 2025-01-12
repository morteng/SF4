import pytest
from datetime import datetime
from freezegun import freeze_time
from app.forms.admin_forms import StipendForm, CustomDateTimeField
from app.constants import FlashMessages
from wtforms import ValidationError

@pytest.mark.parametrize("date_input, is_valid", [
    ("2020-02-29", True),  # Leap year valid date
    ("2021-02-29", False),  # Non-leap year invalid date
    ("2023-02-28", True),  # Non-leap year valid date
])
def test_leap_year_validation(date_input, is_valid):
    if is_valid:
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            pytest.fail(f"Valid date {date_input} failed validation")
    else:
        with pytest.raises(ValueError):
            datetime.strptime(date_input, "%Y-%m-%d")


@pytest.mark.parametrize("time_input", [
    "25:00:00",  # Invalid hour
    "23:60:00",  # Invalid minute
    "23:59:60",  # Invalid second
])
def test_invalid_time_validation(time_input):
    with pytest.raises(ValueError):
        datetime.strptime(time_input, "%H:%M:%S")


def test_custom_date_time_field_invalid_format():
    form = StipendForm(application_deadline="invalid-date")
    assert not form.validate()
    assert FlashMessages.INVALID_DATETIME_FORMAT in form.application_deadline.errors


@freeze_time("2024-02-29")
def test_custom_date_time_field_valid():
    form = StipendForm(application_deadline="2024-02-29 12:00:00")
    assert form.validate()

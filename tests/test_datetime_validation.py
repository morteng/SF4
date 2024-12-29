import pytest
from freezegun import freeze_time
from app.forms.custom_fields import CustomDateTimeField
from app.constants import FlashMessages

@pytest.mark.parametrize("date_str, expected_error", [
    ("2023-02-29 12:00:00", FlashMessages.INVALID_LEAP_YEAR_DATE),
    ("2023-13-01 12:00:00", FlashMessages.INVALID_DATE_VALUES),
    ("2023-01-01 25:00:00", FlashMessages.INVALID_TIME_COMPONENTS),
    ("invalid-date", FlashMessages.INVALID_DATETIME_FORMAT),
    ("", FlashMessages.DATE_REQUIRED),
    ("2023-01-01 12:00:00+99:99", FlashMessages.INVALID_DATETIME_FORMAT),
    ("2023-01-01 12:00:00+00:00", None),  # Valid timezone
    ("2023-01-01 12:00:00", None),  # Valid datetime
    ("2023-04-31 12:00:00", FlashMessages.INVALID_DATE_VALUES),  # April 31st
    ("2023-06-31 12:00:00", FlashMessages.INVALID_DATE_VALUES),  # June 31st
    ("2023-09-31 12:00:00", FlashMessages.INVALID_DATE_VALUES),  # September 31st
    ("2023-11-31 12:00:00", FlashMessages.INVALID_DATE_VALUES),  # November 31st
])
def test_datetime_validation(date_str, expected_error):
    field = CustomDateTimeField()
    field.process_formdata([date_str])
    if expected_error:
        assert str(expected_error) in field.errors
    else:
        assert not field.errors

@freeze_time("2023-01-01")
def test_past_date_validation():
    field = CustomDateTimeField()
    field.process_formdata(["2022-12-31 23:59:59"])
    assert str(FlashMessages.PAST_DATE_REQUIRED) in field.errors

def test_future_date_validation():
    field = CustomDateTimeField()
    field.process_formdata(["2030-01-01 00:00:00"])
    assert str(FlashMessages.FUTURE_DATE_REQUIRED) in field.errors

def test_valid_datetime():
    field = CustomDateTimeField()
    field.process_formdata(["2023-01-01 12:00:00"])
    assert not field.errors

def test_timezone_aware_validation():
    field = CustomDateTimeField()
    field.process_formdata(["2023-01-01 12:00:00+00:00"])
    assert not field.errors

def test_invalid_timezone():
    field = CustomDateTimeField()
    field.process_formdata(["2023-01-01 12:00:00+99:99"])
    assert str(FlashMessages.INVALID_DATETIME_FORMAT) in field.errors

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
])
def test_datetime_validation(date_str, expected_error):
    field = CustomDateTimeField()
    field.process_formdata([date_str])
    assert str(expected_error) in field.errors

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

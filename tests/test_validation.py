import pytest
from datetime import datetime

def test_leap_year_validation():
    """Test February 29th in leap and non-leap years."""
    # Test valid leap year
    try:
        datetime.strptime("2020-02-29", "%Y-%m-%d")
    except ValueError:
        pytest.fail("Valid leap year date failed validation")

    # Test invalid non-leap year
    with pytest.raises(ValueError):
        datetime.strptime("2021-02-29", "%Y-%m-%d")

def test_invalid_time_validation():
    """Test invalid time components."""
    # Test invalid hour
    with pytest.raises(ValueError):
        datetime.strptime("25:00:00", "%H:%M:%S")

    # Test invalid minute
    with pytest.raises(ValueError):
        datetime.strptime("23:60:00", "%H:%M:%S")

    # Test invalid second
    with pytest.raises(ValueError):
        datetime.strptime("23:59:60", "%H:%M:%S")
import pytest
from freezegun import freeze_time
from wtforms import ValidationError
from app.forms.fields import CustomDateTimeField
from app import constants

def test_custom_datetime_field_validation():
    field = CustomDateTimeField()
    
    # Test valid datetime
    field.validate("2023-01-01 12:00:00")
    
    # Test invalid format
    with pytest.raises(ValidationError) as e:
        field.validate("01-01-2023")
    assert str(e.value) == constants.INVALID_DATETIME_FORMAT
    
    # Test leap year
    with pytest.raises(ValidationError) as e:
        field.validate("2023-02-29")
    assert str(e.value) == constants.INVALID_LEAP_YEAR_DATE

@freeze_time("2023-01-01")
def test_time_based_validation():
    field = CustomDateTimeField()
    field.validate("2023-01-01 00:00:00")

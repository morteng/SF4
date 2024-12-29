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

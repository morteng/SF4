import pytest
from app.forms.custom_fields import CustomDateTimeField
from wtforms import ValidationError

def test_custom_date_time_field_valid():
    field = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S")
    field.validate("2023-10-01 12:00:00")  # Should not raise an error

def test_custom_date_time_field_invalid():
    field = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S")
    with pytest.raises(ValidationError):
        field.validate("invalid-date")

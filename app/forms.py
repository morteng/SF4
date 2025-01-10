from datetime import datetime
from wtforms import Field, StringField
from wtforms.validators import InputRequired, Length, Regexp
from app.constants import FlashMessages

class CustomNameField(StringField):
    """Custom field for validating stipend names."""
    
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [
                InputRequired(message=FlashMessages.NAME_REQUIRED),
                Length(max=100, message=FlashMessages.NAME_LENGTH),
                Regexp(r'^[a-zA-Z0-9\s\-.,!?\'"()]+$', 
                      message=FlashMessages.INVALID_NAME_CHARACTERS)
            ]
        super().__init__(label=label, validators=validators, **kwargs)

class OptionalStringField(StringField):
    """Custom field that allows empty strings."""
    
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [
                Optional(),
                Length(max=255, message=FlashMessages.FIELD_TOO_LONG)
            ]
        super().__init__(label=label, validators=validators, **kwargs)

class CustomDateTimeField(Field):
    """Custom field for validating date/time strings."""
    
    def __init__(self, label=None, validators=None, format="%Y-%m-%d %H:%M:%S", **kwargs):
        if validators is None:
            validators = [InputRequired(message=FlashMessages.MISSING_REQUIRED_FIELD)]
        super().__init__(label=label, validators=validators, **kwargs)
        self.format = format

    def validate(self, value):
        """Validate the date/time string."""
        try:
            dt = datetime.strptime(value, self.format)
            # Check for invalid leap year dates
            if dt.month == 2 and dt.day == 29 and not self.is_leap_year(dt.year):
                raise ValueError(FlashMessages.INVALID_LEAP_YEAR)
        except ValueError:
            raise ValueError(FlashMessages.INVALID_DATETIME_FORMAT)

    def is_leap_year(self, year):
        """Check if a year is a leap year."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

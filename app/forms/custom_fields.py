from datetime import datetime
from wtforms import Field, ValidationError, widgets
from wtforms.validators import InputRequired
from app.constants import FlashMessages

class CustomDateTimeField(Field):
    """Consolidated datetime field with multiple format support and validation"""
    widget = widgets.TextInput()

    def __init__(self, label=None, validators=None, formats=None, **kwargs):
        formats = formats or ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
        self.formats = formats
        kwargs.pop('error_messages', None)
        super().__init__(label=label, validators=validators, **kwargs)
        self.validators.append(self._validate_datetime)

    def _validate_datetime(self, form, field):
        """Unified validation handling all formats and leap years"""
        value = field.data
        for fmt in self.formats:
            try:
                dt = datetime.strptime(value, fmt)
                if dt.month == 2 and dt.day == 29 and not self._is_leap_year(dt.year):
                    raise ValidationError(FlashMessages.INVALID_LEAP_YEAR)
                return
            except ValueError:
                continue
        raise ValidationError(f"Invalid datetime format. Use one of: {', '.join(self.formats)}")

    def _is_leap_year(self, year):
        """Check if a year is a leap year."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def _value(self):
        return self.data.strftime(self.formats[0]) if self.data else ''

    def _value(self):
        """Return the formatted string representation of the field's data.
        
        This method is required by WTForms for proper template rendering.
        """
        if self.data:
            return self.data.strftime(self.format)
        return ''

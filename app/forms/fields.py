import re
from datetime import datetime
from wtforms.fields import Field, SelectField
from wtforms.validators import ValidationError, InputRequired
from app.constants import FlashMessages

class CustomDateTimeField(Field):
    """Custom field for date/time validation with comprehensive checks."""
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired(message=FlashMessages.DATE_REQUIRED)]
        super().__init__(label=label, validators=validators, **kwargs)
        self.render_kw = {'placeholder': 'YYYY-MM-DD HH:MM:SS'}

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
            try:
                # Parse and validate the datetime
                dt = datetime.strptime(self.data, '%Y-%m-%d %H:%M:%S')
                
                # Validate time components
                if not (0 <= dt.hour < 24 and 0 <= dt.minute < 60 and 0 <= dt.second < 60):
                    raise ValidationError(FlashMessages.INVALID_TIME_VALUES)
                
                # Validate leap year
                if dt.month == 2 and dt.day == 29:
                    if not self._is_leap_year(dt.year):
                        raise ValidationError(FlashMessages.INVALID_LEAP_YEAR)
                
                # Validate future date
                if dt < datetime.now():
                    raise ValidationError(FlashMessages.PAST_DATE)
                
                # Validate future date limit (5 years)
                max_future = datetime.now().replace(year=datetime.now().year + 5)
                if dt > max_future:
                    raise ValidationError(FlashMessages.FUTURE_DATE_LIMIT)
                    
            except ValueError:
                raise ValidationError(FlashMessages.INVALID_DATE_FORMAT)

    def _is_leap_year(self, year):
        """Helper method to check if a year is a leap year."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

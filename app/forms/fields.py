import re
from wtforms.fields import DateTimeField, SelectField
from wtforms.validators import ValidationError
from datetime import datetime
import pytz
from pytz import timezone, utc

class CustomDateTimeField(DateTimeField):
    """Custom DateTimeField with timezone support and enhanced validation."""
    """Custom DateTimeField with timezone support and enhanced validation."""
    """Custom DateTimeField with timezone support and enhanced validation."""
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', timezone='UTC', **kwargs):
        # Extract error_messages from kwargs to avoid passing it to Field.__init__()
        error_messages = kwargs.pop('error_messages', {})
        super().__init__(label, validators, format=format, **kwargs)
        self.format = format
        self.timezone_str = str(timezone) if timezone else 'UTC'
        self._invalid_leap_year = False  # Track invalid leap year state
        # Initialize default error messages
        self.error_messages = {
            'invalid_format': 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS',
            'invalid_date': 'Invalid date values (e.g., Feb 30)',
            'invalid_time': 'Invalid time values (e.g., 25:61:61)',
            'missing_time': 'Time is required. Please use YYYY-MM-DD HH:MM:SS',
            'required': 'Date is required',
            'invalid_leap_year': 'Invalid date values (e.g., Feb 29 in non-leap years)'
        }
        # Update with any custom error messages passed in
        self.error_messages.update(error_messages)

    def process_formdata(self, valuelist):
        if not valuelist or not valuelist[0]:
            self.errors = []  # Clear any existing errors
            # Use our custom error message instead of the default
            self.errors.append(self.error_messages.get('required', 'Date is required.'))
            self.data = None
            self._invalid_leap_year = False
            return False  # Explicitly return False to prevent further validation
            
        date_str = valuelist[0].strip()
        if not date_str:
            self.errors.append(self.error_messages['required'])
            self.data = None
            return
            
        date_str = valuelist[0]
        self._invalid_leap_year = False  # Reset leap year flag
            
        # First check for leap year dates
        if '02-29' in date_str:
            try:
                # Extract just the date portion
                date_part = date_str.split()[0]
                parsed_date = datetime.strptime(date_part, '%Y-%m-%d')
                if parsed_date.month == 2 and parsed_date.day == 29:
                    year = parsed_date.year
                    is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
                    if not is_leap:
                        self.errors = []
                        self.errors.append(self.error_messages['invalid_leap_year'])
                        self.data = None
                        self._invalid_leap_year = True
                        return  # Stop processing if invalid leap year
            except ValueError as e:
                # If we can't parse the date, check if it's a leap year case
                if '02-29' in date_str:
                    self.errors = []
                    self.errors.append(self.error_messages['invalid_leap_year'])
                    self.data = None
                    self._invalid_leap_year = True
                    return
                else:
                    # For other date errors, use the standard error message
                    self.errors = []
                    self.errors.append(self.error_messages['invalid_date'])
                    self.data = None
                    self._invalid_leap_year = False
                    return
            # First check if the date string matches the expected format
            if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', date_str):
                self.errors.append(self.error_messages['invalid_format'])
                self.data = None
                return

            try:
                # Try to parse the full date string
                parsed_dt = datetime.strptime(date_str, self.format)

                # Validate time components
                if not self._validate_time_components(parsed_dt):
                    return

                # Validate date components
                if not self._validate_date_components(parsed_dt):
                    return

                # If all validations pass, proceed with timezone handling
                local_tz = timezone(self.timezone_str)
                local_dt = local_tz.localize(parsed_dt, is_dst=None)
                self.data = local_dt.astimezone(utc)
                self.raw_value = date_str

            except ValueError as e:
                error_str = str(e)

                # Handle specific error cases
                if 'does not match format' in error_str:
                    self.errors.append(self.error_messages['invalid_format'])
                elif 'day is out of range' in error_str or 'month is out of range' in error_str:
                    self.errors.append(self.error_messages['invalid_date'])
                elif 'hour must be in' in error_str or 'minute must be in' in error_str or 'second must be in' in error_str:
                    self.errors.append(self.error_messages['invalid_time'])
                else:
                    self.errors.append(self.error_messages['invalid_date'])
            except pytz.UnknownTimeZoneError:
                self.errors.append(self.error_messages['invalid_timezone'])

    def _validate_time_components(self, dt):
        try:
            # Check if time components are valid
            if dt.hour < 0 or dt.hour > 23:
                self.errors.append(self.error_messages['invalid_time'])
                return False
            if dt.minute < 0 or dt.minute > 59:
                self.errors.append(self.error_messages['invalid_time'])
                return False
            if dt.second < 0 or dt.second > 59:
                self.errors.append(self.error_messages['invalid_time'])
                return False
            return True
        except ValueError:
            self.errors.append(self.error_messages['invalid_time'])
            return False

    def validate(self, form, extra_validators=()):
        # If we already have errors from process_formdata, return False
        if self.errors:
            return False
            
        # Then proceed with normal validation
        result = super().validate(form, extra_validators)
        
        # If validation failed and we have a required field error, replace it with our custom message
        if not result and 'This field is required.' in self.errors:
            self.errors.remove('This field is required.')
            self.errors.append(self.error_messages.get('required', 'Date is required'))
            
        return result
        
    def _validate_date_components(self, dt):
        try:
            # Check if the date components are valid
            dt.replace(hour=0, minute=0, second=0)
            dt.time()
            
            # Additional validation for edge cases
            if dt.year < 1900 or dt.year > 2100:
                raise ValidationError(self.error_messages['invalid_date'])
                
            # Check for invalid month/day combinations
            try:
                # General date validation
                datetime(dt.year, dt.month, dt.day)
            except ValueError:
                raise ValidationError(self.error_messages['invalid_date'])
                
            # Check leap year flag
            if self._invalid_leap_year:
                raise ValidationError(self.error_messages['invalid_leap_year'])
                
            return True
        except ValueError:
            raise ValidationError(self.error_messages['invalid_date'])

    def _value(self):
        if hasattr(self, 'raw_value'):
            return self.raw_value
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

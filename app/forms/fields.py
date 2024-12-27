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
        super().__init__(label, validators, format=format, **kwargs)
        self.format = format
        self.timezone_str = str(timezone) if timezone else 'UTC'
        self.error_messages = {
            'invalid_format': 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS',
            'invalid_date': 'Invalid date values (e.g., Feb 30)',
            'invalid_time': 'Invalid time values (e.g., 25:61:61)',
            'missing_time': 'Time is required. Please use YYYY-MM-DD HH:MM:SS',
            'required': 'Date is required',
            'invalid_leap_year': 'Invalid date values (e.g., Feb 30)'
        }
        self.errors = []

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = valuelist[0]
            if not date_str:
                self.errors.append(self.error_messages['required'])
                return
            
            try:
                # First try parsing the date string
                parsed_dt = datetime.strptime(date_str, self.format)
                
                # Validate date components
                self._validate_date_components(parsed_dt)
                
                # Validate time components
                self._validate_time_components(parsed_dt)
                
                # If parsing succeeds, proceed with timezone handling
                local_tz = timezone(self.timezone_str)
                local_dt = local_tz.localize(parsed_dt, is_dst=None)
                self.data = local_dt.astimezone(utc)
                # Store the raw string value for form display
                self.raw_value = date_str
                
            except ValueError as e:
                error_str = str(e)
                if 'does not match format' in error_str:
                    self.errors = [self.error_messages['invalid_format']]
                elif 'day is out of range' in error_str or 'month is out of range' in error_str or 'day must be in' in error_str:
                    self.errors = [self.error_messages['invalid_date']]
                elif 'hour must be in' in error_str or 'minute must be in' in error_str or 'second must be in' in error_str:
                    self.errors = [self.error_messages['invalid_time']]
                else:
                    self.errors = [self.error_messages['invalid_date']]
            except ValidationError as e:
                self.errors = [str(e)]
            except pytz.UnknownTimeZoneError:
                self.errors = [self.error_messages['invalid_timezone']]

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

    def _validate_date_components(self, dt):
        try:
            # Check if the date components are valid
            dt.replace(hour=0, minute=0, second=0)
            dt.time()
            
            # Additional validation for edge cases
            if dt.year < 1900 or dt.year > 2100:
                self.errors.append(self.error_messages['invalid_date'])
                return False
                
            # Check for invalid month/day combinations
            try:
                # Check for February 29th in non-leap years
                if dt.month == 2 and dt.day == 29:
                    # Check if it's a leap year
                    is_leap = (dt.year % 4 == 0 and dt.year % 100 != 0) or (dt.year % 400 == 0)
                    if not is_leap:
                        self.errors = [self.error_messages['invalid_leap_year']]
                        return False
                
                # General date validation
                datetime(dt.year, dt.month, dt.day)
            except ValueError:
                if dt.month == 2 and dt.day == 29:
                    self.errors = [self.error_messages['invalid_leap_year']]
                else:
                    self.errors.append(self.error_messages['invalid_date'])
                return False
                
            return True
        except ValueError:
            self.errors.append(self.error_messages['invalid_date'])
            return False

    def _value(self):
        if hasattr(self, 'raw_value'):
            return self.raw_value
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

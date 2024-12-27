from wtforms.fields import DateTimeField, SelectField
from wtforms.validators import ValidationError
from datetime import datetime
import pytz
from pytz import timezone, utc

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', timezone='UTC', **kwargs):
        super().__init__(label, validators, format=format, **kwargs)
        self.format = format
        self.timezone = SelectField(
            'Timezone',
            choices=[(tz, tz) for tz in pytz.all_timezones],
            default='UTC'
        )
        self.error_messages = {
            'invalid_format': 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS',
            'invalid_date': 'Invalid date values (e.g., Feb 30)',
            'invalid_time': 'Invalid time values (e.g., 25:61:61)',
            'missing_time': 'Time is required. Please use YYYY-MM-DD HH:MM:SS',
            'required': 'This field is required',
            'invalid_timezone': 'Invalid timezone selected',
            'daylight_saving': 'Ambiguous time due to daylight saving transition',
            'timezone_conversion': 'Error converting to UTC',
            'future_date': 'Date must be in the future',
            'past_date': 'Date must be in the past'
        }
        # Initialize errors as a list
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
                if not self._validate_date_components(parsed_dt):
                    return
                
                # If parsing succeeds, proceed with timezone handling
                local_tz = timezone(self.timezone)
                local_dt = local_tz.localize(parsed_dt, is_dst=None)
                self.data = local_dt.astimezone(utc)
                
            except ValueError as e:
                error_str = str(e)
                if 'does not match format' in error_str:
                    self.errors.append(self.error_messages['invalid_format'])
                elif 'day is out of range' in error_str:
                    self.errors.append(self.error_messages['invalid_date'])
                elif 'month is out of range' in error_str:
                    self.errors.append(self.error_messages['invalid_date'])
                elif 'hour must be in' in error_str:
                    self.errors.append(self.error_messages['invalid_time'])
                elif 'minute must be in' in error_str:
                    self.errors.append(self.error_messages['invalid_time'])
                elif 'second must be in' in error_str:
                    self.errors.append(self.error_messages['invalid_time'])
                else:
                    self.errors.append(self.error_messages['invalid_date'])
            except pytz.UnknownTimeZoneError:
                self.errors.append(self.error_messages['invalid_timezone'])

    def _validate_date_components(self, dt):
        try:
            # Check if the date components are valid
            dt.replace(hour=0, minute=0, second=0)
            dt.time()
            
            # Additional validation for edge cases
            if dt.year < 1900 or dt.year > 2100:
                self.errors.append(self.error_messages['invalid_date'])
                return False
                
            return True
        except ValueError:
            self.errors.append(self.error_messages['invalid_date'])
            return False

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

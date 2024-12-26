from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime
import pytz
from pytz import timezone, utc

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', timezone='UTC', **kwargs):
        super().__init__(label, validators, format=format, **kwargs)
        self.format = format
        self.timezone = timezone
        self.error_messages = {
            'invalid_format': 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS',
            'invalid_date': 'Invalid date values (e.g., Feb 30)',
            'invalid_time': 'Invalid time values (e.g., 25:61:61)',
            'missing_time': 'Time is required. Please use YYYY-MM-DD HH:MM:SS',
            'required': 'Date is required',
            'invalid_timezone': 'Invalid timezone',
            'daylight_saving': 'Ambiguous time due to daylight saving transition',
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
                # Parse in local timezone
                local_tz = timezone(self.timezone)
                naive_dt = datetime.strptime(date_str, self.format)
                local_dt = local_tz.localize(naive_dt, is_dst=None)
                
                # Convert to UTC for storage
                self.data = local_dt.astimezone(utc)
                
                # Validate components
                if not self._validate_date_components(self.data):
                    self.errors.append(self.error_messages['invalid_date'])
                    
            except Exception as e:
                if isinstance(e, ValueError):
                    if 'does not match format' in str(e):
                        self.errors.append(self.error_messages['invalid_format'])
                    elif 'day is out of range' in str(e):
                        self.errors.append(self.error_messages['invalid_date'])
                    elif 'is ambiguous' in str(e):
                        self.errors.append(self.error_messages['daylight_saving'])
                elif isinstance(e, pytz.UnknownTimeZoneError):
                    self.errors.append(self.error_messages['invalid_timezone'])
                else:
                    self.errors.append(self.error_messages['invalid_date'])

    def _validate_date_components(self, dt):
        try:
            # Check if the date components are valid
            dt.replace(hour=0, minute=0, second=0)
            dt.time()
            
            # Additional validation for edge cases
            if dt.year < 1900 or dt.year > 2100:
                self.errors.append('Year must be between 1900 and 2100')
                return False
                
            if dt.month < 1 or dt.month > 12:
                self.errors.append('Month must be between 1 and 12')
                return False
                
            if dt.day < 1 or dt.day > 31:
                self.errors.append('Day must be between 1 and 31')
                return False
                
            if dt.hour < 0 or dt.hour > 23:
                self.errors.append('Hour must be between 0 and 23')
                return False
                
            if dt.minute < 0 or dt.minute > 59:
                self.errors.append('Minute must be between 0 and 59')
                return False
                
            if dt.second < 0 or dt.second > 59:
                self.errors.append('Second must be between 0 and 59')
                return False
                
            return True
        except ValueError:
            return False

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

import re
from wtforms.fields import DateTimeField, SelectField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    """
    Custom DateTimeField with enhanced validation features.
    
    Features:
    - Timezone support
    - Strict format validation (YYYY-MM-DD HH:MM:SS)
    - Future/past date validation
    - Leap year validation
    - Custom error messages
    """
    
    # Define error messages
    error_messages = {
        'invalid_format': 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS',
        'invalid_date': 'Invalid date values (e.g., Feb 30)',
        'invalid_time': 'Invalid time values (e.g., 25:61:61)',
        'missing_time': 'Time is required. Please use YYYY-MM-DD HH:MM:SS',
        'required': 'Date is required',
        'invalid_leap_year': 'Invalid date values (e.g., Feb 29 in non-leap years)',
        'past_date': 'Application deadline must be a future date',
        'future_date': 'Application deadline cannot be more than 5 years in the future'
    }
    
    def __init__(self, *args, **kwargs):
        self.timezone = kwargs.pop('timezone', None)
        # Merge custom error messages with defaults
        custom_messages = kwargs.pop('error_messages', {})
        self.error_messages = {**self.error_messages, **custom_messages}
        kwargs['format'] = '%Y-%m-%d %H:%M:%S'
        kwargs['render_kw'] = {'placeholder': 'YYYY-MM-DD HH:MM:SS'}
        super().__init__(*args, **kwargs)
        
    def _is_empty_value(self, value):
        """Check if the value is empty or whitespace only."""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False


    def process_formdata(self, valuelist):
        # Clear any existing errors
        self.errors = []
        
        # First check if value is missing or empty
        if not valuelist or self._is_empty_value(valuelist[0]):
            self.errors.append('Application deadline is required.')
            self.data = None
            return
            
        # Continue with format validation if value exists
        date_str = valuelist[0].strip()
        if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', date_str):
            self.errors.append('Invalid date format. Please use YYYY-MM-DD HH:MM:SS')
            self.data = None
            return
            
        # Validate date components
        try:
            datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            self.errors.append('Invalid date values')
            self.data = None
            return
            
        # Continue with format validation if value exists
        date_str = valuelist[0].strip()
        if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', date_str):
            self.errors.append(self.error_messages.get('invalid_format', 'Invalid date format'))
            self.data = None
            return
            
        # Validate date components
        try:
            datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            self.errors.append(self.error_messages.get('invalid_date', 'Invalid date values'))
            self.data = None
            return
            
            
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

                # If all validations pass, store the datetime
                self.data = parsed_dt
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
            except ValueError as e:
                error_str = str(e)
                if 'does not match format' in error_str:
                    self.errors.append(self.error_messages['invalid_format'])
                elif 'day is out of range' in error_str or 'month is out of range' in error_str:
                    self.errors.append(self.error_messages['invalid_date'])
                elif 'hour must be in' in error_str or 'minute must be in' in error_str or 'second must be in' in error_str:
                    self.errors.append(self.error_messages['invalid_time'])
                else:
                    self.errors.append(self.error_messages['invalid_date'])

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
        # Initialize errors as list if needed
        if not hasattr(self, 'errors') or isinstance(self.errors, tuple):
            self.errors = []
            
        # If data is empty, return required error
        if not self.data:
            self.errors.append('Application deadline is required.')
            return False
    
        # If we already have errors from process_formdata, return False
        if self.errors:
            return False
            
        # Validate the format first
        if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', str(self.data)):
            self.errors.append(self.error_messages.get(
                'invalid_format', 
                'Invalid date format. Please use YYYY-MM-DD HH:MM:SS'
            ))
            return False
            
        # Validate date components
        try:
            dt = datetime.strptime(str(self.data), '%Y-%m-%d %H:%M:%S')
            
            # Validate time components
            if not (0 <= dt.hour <= 23 and 
                    0 <= dt.minute <= 59 and 
                    0 <= dt.second <= 59):
                self.errors.append(self.error_messages.get('invalid_time', 'Invalid time values'))
                return False
                
            # Validate date components
            try:
                datetime(dt.year, dt.month, dt.day)
            except ValueError:
                self.errors.append(self.error_messages.get('invalid_date', 'Invalid date values'))
                return False
                
        except ValueError:
            self.errors.append('Invalid date values')
            return False
            
        # Validate date components
        try:
            dt = datetime.strptime(str(self.data), '%Y-%m-%d %H:%M:%S')
            
            # Validate time components
            if not (0 <= dt.hour <= 23 and 
                    0 <= dt.minute <= 59 and 
                    0 <= dt.second <= 59):
                self.errors.append(self.error_messages.get('invalid_time', 'Invalid time values'))
                return False
                
            # Validate date components
            try:
                datetime(dt.year, dt.month, dt.day)
            except ValueError:
                self.errors.append(self.error_messages.get('invalid_date', 'Invalid date values'))
                return False
        except ValueError:
            self.errors.append(self.error_messages.get('invalid_date', 'Invalid date values'))
            return False
            
        # Validate date components
        try:
            dt = datetime.strptime(str(self.data), '%Y-%m-%d %H:%M:%S')
            
            # Validate time components
            if not (0 <= dt.hour <= 23 and 
                    0 <= dt.minute <= 59 and 
                    0 <= dt.second <= 59):
                self.errors.append(self.error_messages.get(
                    'invalid_time',
                    'Invalid time values (e.g., 25:61:61)'
                ))
                return False
                
            # Validate date components
            try:
                datetime(dt.year, dt.month, dt.day)
            except ValueError:
                self.errors.append(self.error_messages.get(
                    'invalid_date',
                    'Invalid date values (e.g., Feb 30)'
                ))
                return False
                
            # Check for leap year
            if dt.month == 2 and dt.day == 29:
                if not (dt.year % 4 == 0 and (dt.year % 100 != 0 or dt.year % 400 == 0)):
                    self.errors.append(self.error_messages.get(
                        'invalid_leap_year',
                        'Invalid date values (e.g., Feb 29 in non-leap years)'
                    ))
                    return False
                    
            # Validate future date
            now = datetime.now()
            if dt < now:
                self.errors.append(self.error_messages.get(
                    'past_date',
                    'Application deadline must be a future date'
                ))
                return False
                
            # Validate future date limit (5 years)
            max_future = now.replace(year=now.year + 5)
            if dt > max_future:
                self.errors.append(self.error_messages.get(
                    'future_date',
                    'Application deadline cannot be more than 5 years in the future'
                ))
                return False
                
        except ValueError:
            self.errors.append(self.error_messages.get(
                'invalid_date',
                'Invalid date values'
            ))
            return False
            
        return True
        
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
                
            # Add future date validation
            now = datetime.now()
            if dt < now:
                raise ValidationError(self.error_messages['past_date'])
                
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

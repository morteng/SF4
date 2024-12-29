import re
from wtforms.fields import DateTimeField, SelectField
from wtforms.validators import ValidationError
from datetime import datetime
from app.constants import FlashMessages

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        # Initialize with default error messages from constants
        kwargs.setdefault('error_messages', {
            'required': str(FlashMessages.DATE_REQUIRED),
            'invalid_format': str(FlashMessages.INVALID_DATETIME_FORMAT),
            'invalid_time': str(FlashMessages.INVALID_TIME_COMPONENTS),
            'invalid_leap_year': str(FlashMessages.INVALID_LEAP_YEAR_DATE),
            'invalid_date': str(FlashMessages.INVALID_DATE_VALUES),
            'past_date': str(FlashMessages.PAST_DATE),
            'future_date': str(FlashMessages.FUTURE_DATE),
        })
        
        super().__init__(label=label, validators=validators, format=format, **kwargs)
        self.render_kw = {'placeholder': 'YYYY-MM-DD HH:MM:SS'}
        self._format = format

    def _validate_time_components(self, dt):
        """Validate time components (hours, minutes, seconds)"""
        if not (0 <= dt.hour <= 23 and 
                0 <= dt.minute <= 59 and 
                0 <= dt.second <= 59):
            raise ValidationError(self.error_messages['invalid_time'])

    def process_formdata(self, valuelist):
        if not valuelist or not valuelist[0].strip():
            self.data = None
            return
            
        date_str = valuelist[0]
        try:
            parsed_dt = datetime.strptime(date_str, self.format)
            
            # Validate date components
            try:
                datetime(parsed_dt.year, parsed_dt.month, parsed_dt.day)
            except ValueError:
                raise ValidationError(self.error_messages['invalid_date'])
                
            # Validate time components
            self._validate_time_components(parsed_dt)
                
            # Leap year validation
            if parsed_dt.month == 2 and parsed_dt.day == 29:
                try:
                    datetime(parsed_dt.year, 2, 29)
                except ValueError:
                    raise ValidationError(self.error_messages['invalid_leap_year'])
                    
            # Future date validation
            now = datetime.now()
            if parsed_dt < now:
                raise ValidationError(self.error_messages['past_date'])
                
            self.data = parsed_dt
            self.raw_value = date_str
            
        except ValidationError:
            raise
        except ValueError as e:
            error_str = str(e)
            if 'does not match format' in error_str:
                raise ValidationError(self.error_messages['invalid_format'])
            elif 'day is out of range' in error_str or 'month is out of range' in error_str:
                raise ValidationError(self.error_messages['invalid_date'])
            else:
                raise ValidationError(self.error_messages['invalid_date'])

    @classmethod
    def benchmark_validation(cls, iterations=1000):
        """Benchmark validation performance"""
        import time
        test_cases = [
            ('2024-12-31 23:59:59', True),  # Valid
            ('2024-02-29 00:00:00', True),  # Leap year
            ('2023-02-29 00:00:00', False), # Invalid leap year
            ('2024-13-01 00:00:00', False), # Invalid month
            ('2024-12-32 00:00:00', False), # Invalid day
            ('2024-12-31 24:00:00', False), # Invalid hour
            ('2024-12-31 23:60:00', False), # Invalid minute
            ('2024-12-31 23:59:60', False), # Invalid second
        ]
        
        field = cls()
        results = {}
        
        for value, expected in test_cases:
            start = time.perf_counter()
            for _ in range(iterations):
                field.process_formdata([value])
            elapsed = time.perf_counter() - start
            results[value] = {
                'time': elapsed,
                'iterations': iterations,
                'valid': expected,
                'actual': field.data is not None
            }
            
        return results

    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        # Store format in a private variable
        self._format = format if isinstance(format, str) else '%Y-%m-%d %H:%M:%S'
        
        # Initialize error messages
        self.error_messages = {
            'required': str(FlashMessages.DATE_REQUIRED),
            'invalid_format': str(FlashMessages.INVALID_DATE_FORMAT),
            'invalid_time': str(FlashMessages.INVALID_TIME_VALUES),
            'invalid_leap_year': str(FlashMessages.INVALID_LEAP_YEAR),
            'invalid_date': str(FlashMessages.INVALID_DATE_VALUES),
            'past_date': str(FlashMessages.PAST_DATE),
            'future_date': str(FlashMessages.FUTURE_DATE),
            **kwargs.pop('error_messages', {})
        }
        
        # Call parent __init__ without passing format
        super().__init__(label=label, validators=validators, **kwargs)
        self.render_kw = {'placeholder': 'YYYY-MM-DD HH:MM:SS'}

    @property
    def format(self):
        """Getter for format that ensures it's always a string"""
        return self._format

    @format.setter
    def format(self, value):
        """Setter for format that ensures it's always a string"""
        self._format = value if isinstance(value, str) else '%Y-%m-%d %H:%M:%S'
    def _is_empty_value(self, value):
        """Check if the value is empty or whitespace only."""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False


    def process_formdata(self, valuelist):
        if not valuelist or not valuelist[0].strip():
            self.data = None
            return
            
        date_str = valuelist[0]
        try:
            # Optimized parsing and validation
            parsed_dt = datetime.strptime(date_str, self._format)
            
            # Validate date components first (cheaper operation)
            try:
                datetime(parsed_dt.year, parsed_dt.month, parsed_dt.day)
            except ValueError:
                self.errors.append(self.error_messages['invalid_date'])
                self.data = None
                return
                
            # Then validate time components
            if not (0 <= parsed_dt.hour <= 23 and 
                    0 <= parsed_dt.minute <= 59 and 
                    0 <= parsed_dt.second <= 59):
                self.errors.append(self.error_messages['invalid_time'])
                self.data = None
                return
                
            # Leap year validation only when needed
            if parsed_dt.month == 2 and parsed_dt.day == 29:
                try:
                    datetime(parsed_dt.year, 2, 29)
                except ValueError:
                    self.errors.append(self.error_messages['invalid_leap_year'])
                    self.data = None
                    return
                    
            # Future date validation
            now = datetime.now()
            if parsed_dt < now:
                self.errors.append(self.error_messages['past_date'])
                self.data = None
                return
                
            # Future date limit (5 years)
            max_future = now.replace(year=now.year + 5)
            if parsed_dt > max_future:
                self.errors.append(self.error_messages['future_date'])
                self.data = None
                return
                
            self.data = parsed_dt
            self.raw_value = date_str
            
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
            self.data = None


    def _value(self):
        if hasattr(self, 'raw_value'):
            return self.raw_value
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        super().__init__(label, validators, format=format, **kwargs)
        self.format = format
        self.error_messages = {
            'invalid_format': 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS',
            'invalid_date': 'Invalid date values (e.g., Feb 30)',
            'invalid_time': 'Invalid time values (e.g., 25:61:61)',
            'missing_time': 'Time is required. Please use YYYY-MM-DD HH:MM:SS',
            'required': 'Date is required'
        }

    def process_formdata(self, valuelist):
        if not valuelist or not valuelist[0].strip():
            self.errors.append(self.error_messages['required'])
            self.data = None
            return
            
        date_str = valuelist[0].strip()
        try:
            dt = datetime.strptime(date_str, self.format)
            
            # Validate date components
            if dt.month < 1 or dt.month > 12:
                raise ValueError('invalid_date')
            if dt.day < 1 or dt.day > 31:
                raise ValueError('invalid_date')
            if dt.month in [4, 6, 9, 11] and dt.day > 30:
                raise ValueError('invalid_date')
            if dt.month == 2:
                # Handle leap years
                if dt.year % 4 == 0 and (dt.year % 100 != 0 or dt.year % 400 == 0):
                    if dt.day > 29:
                        raise ValueError('invalid_date')
                elif dt.day > 28:
                    raise ValueError('invalid_date')
            
            # Validate time components
            if dt.hour < 0 or dt.hour > 23:
                raise ValueError('invalid_time')
            if dt.minute < 0 or dt.minute > 59:
                raise ValueError('invalid_time')
            if dt.second < 0 or dt.second > 59:
                raise ValueError('invalid_time')
            
            self.data = dt
            
        except ValueError as e:
            self.data = None
            error_str = str(e)
            
            if error_str == 'invalid_date':
                self.errors.append(self.error_messages['invalid_date'])
            elif error_str == 'invalid_time':
                self.errors.append(self.error_messages['invalid_time'])
            elif 'unconverted data remains' in error_str:
                self.errors.append(self.error_messages['missing_time'])
            elif 'does not match format' in error_str:
                self.errors.append(self.error_messages['invalid_format'])
            else:
                self.errors.append(self.error_messages['invalid_date'])

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

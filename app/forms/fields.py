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
            self.data = datetime.strptime(date_str, self.format)
        except ValueError as e:
            self.data = None
            error_str = str(e)
            
            if 'unconverted data remains' in error_str:
                self.errors.append(self.error_messages['missing_time'])
            elif 'does not match format' in error_str:
                self.errors.append(self.error_messages['invalid_format'])
            else:
                # Handle invalid date/time values
                try:
                    # Try parsing just the date portion
                    datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                    # If date is valid, it must be an invalid time
                    self.errors.append(self.error_messages['invalid_time'])
                except ValueError:
                    self.errors.append(self.error_messages['invalid_date'])

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

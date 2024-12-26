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
        # Initialize errors as a list
        self.errors = []

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = valuelist[0]
            if not date_str:
                self.errors.append(self.error_messages['required'])
                return
            try:
                self.data = datetime.strptime(date_str, self.format)
            except ValueError as e:
                if 'unconverted data remains' in str(e):
                    self.errors.append(self.error_messages['missing_time'])
                elif 'does not match format' in str(e):
                    self.errors.append(self.error_messages['invalid_format'])
                else:
                    self.errors.append(self.error_messages['invalid_date'])

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

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
        if valuelist:
            date_str = valuelist[0].strip()
            if not date_str:
                raise ValidationError(self.error_messages['required'])
            
            try:
                # First try parsing the full datetime
                self.data = datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                # Check if it's just a date without time
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                    raise ValidationError(self.error_messages['missing_time'])
                except ValueError:
                    # Check if it's invalid date components
                    try:
                        datetime.strptime(date_str[:10], '%Y-%m-%d')
                        raise ValidationError(self.error_messages['invalid_time'])
                    except ValueError:
                        raise ValidationError(self.error_messages['invalid_date'])

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

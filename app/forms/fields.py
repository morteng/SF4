from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        super().__init__(label, validators, format=format, **kwargs)
        self.format = format

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = valuelist[0]  # Use first value only
            try:
                self.data = datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise ValidationError(f'Invalid date format. Please use {self.format}.')

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        if self.data:
            return self.data.strftime(self.format)
        return ""

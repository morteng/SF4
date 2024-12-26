from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d', **kwargs):
        super().__init__(label, validators, format=format, **kwargs)
        self.format = format
        self.raw_data = []

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        return self.data and self.data.strftime(self.format) or ''

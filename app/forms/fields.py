from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d', **kwargs):
        super().__init__(label, validators, **kwargs)
        self.format = format

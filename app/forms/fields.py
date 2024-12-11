from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        super(CustomDateTimeField, self).__init__(label, validators, **kwargs)
        if isinstance(format, list):
            self.format = format[0]  # Use the first format in the list
        else:
            self.format = format

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise ValidationError('Invalid date format. Please use YYYY-MM-DD HH:MM:SS.')

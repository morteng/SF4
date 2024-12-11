from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise ValidationError('Invalid date format. Please use YYYY-MM-DD HH:MM:SS.')

from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            # Handle self.format as list or string
            if isinstance(self.format, (list, tuple)):
                formats = self.format
            else:
                formats = [self.format]
            for fmt in formats:
                try:
                    self.data = datetime.strptime(date_str, fmt)
                    return
                except ValueError:
                    continue
            self.data = None
            raise ValidationError('Invalid date format. Please use YYYY-MM-DD HH:MM:SS.')

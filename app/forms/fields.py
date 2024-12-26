from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
import logging
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        super(CustomDateTimeField, self).__init__(label, validators, **kwargs)
        if isinstance(format, list):
            self.format = format  # Keep the list intact for compatibility
        else:
            self.format = [format]  # Convert single string to a list

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            for fmt in self.format:
                try:
                    self.data = datetime.strptime(date_str, fmt)
                    return
                except ValueError:
                    logging.info(f"Invalid date format: {date_str} with format {fmt}")
                    continue
            self.data = None
            raise ValidationError(f"Invalid date format. Please use one of the following: {', '.join(self.format)}.")

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        return self.data.strftime(self.format[0]) if self.data else ""

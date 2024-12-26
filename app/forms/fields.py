from wtforms.fields import DateTimeField
from wtforms.validators import ValidationError
from datetime import datetime

class CustomDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', **kwargs):
        super().__init__(label, validators, **kwargs)
        self.format = format
        self.process_formdata = self._process_formdata

    def _process_formdata(self, valuelist):
        if valuelist:
            date_str = valuelist[0]
            try:
                self.data = datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Invalid date format'))

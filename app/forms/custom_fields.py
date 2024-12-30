from datetime import datetime
from wtforms import Field, ValidationError
from wtforms.validators import InputRequired
from app.constants import FlashMessages

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, format="%Y-%m-%d %H:%M:%S", **kwargs):
        if validators is None:
            validators = [InputRequired(message="This field is required")]
        self.format = format
        super().__init__(label=label, validators=validators, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise ValidationError(f'Invalid date format. Use {self.format}')

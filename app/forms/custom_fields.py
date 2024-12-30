from datetime import datetime
from wtforms import Field, ValidationError
from wtforms.validators import InputRequired
from app.constants import FlashMessages

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, format="%Y-%m-%d %H:%M:%S", **kwargs):
        if validators is None:
            validators = [InputRequired(message=FlashMessages.MISSING_FIELD_ERROR.value)]
        self.format = format
        # Remove error_messages from kwargs if present
        kwargs.pop('error_messages', None)
        super().__init__(label=label, validators=validators, **kwargs)

    def process_formdata(self, valuelist):
        if not valuelist or not valuelist[0].strip():
            self.data = None
            return
            
        date_str = valuelist[0]
        try:
            self.data = datetime.strptime(date_str, self.format)
        except ValueError:
            raise ValidationError(FlashMessages.INVALID_DATETIME_FORMAT.value)

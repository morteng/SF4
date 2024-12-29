from wtforms import Field
from wtforms.validators import InputRequired
from datetime import datetime
from wtforms import ValidationError
from app.constants import FlashMessages

class CustomDateTimeField(Field):
    """Custom datetime field that validates and parses datetime strings."""
    
    def __init__(self, label=None, validators=None, format="%Y-%m-%d %H:%M:%S", **kwargs):
        """Initialize the datetime field."""
        if validators is None:
            validators = [InputRequired(message=FlashMessages.MISSING_FIELD_ERROR.value)]
        self.format = format
        super().__init__(label=label, validators=validators, **kwargs)
        # Store error messages in a way compatible with WTForms
        self.error_messages = {
            'invalid': FlashMessages.INVALID_DATETIME_FORMAT.value,
            'required': FlashMessages.MISSING_FIELD_ERROR.value
        }

    def process_formdata(self, valuelist):
        """Process form data into a datetime object."""
        if not valuelist or not valuelist[0].strip():
            self.data = None
            return
            
        date_str = valuelist[0]
        try:
            self.data = datetime.strptime(date_str, self.format)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])

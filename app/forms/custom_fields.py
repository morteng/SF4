from datetime import datetime
from wtforms import ValidationError
from app import constants

class CustomDateTimeField:
    def __init__(self, format="%Y-%m-%d %H:%M:%S"):
        self.format = format

    def validate(self, value):
        try:
            datetime.strptime(value, self.format)
        except ValueError:
            raise ValidationError(constants.INVALID_DATETIME_FORMAT)
from datetime import datetime
from wtforms import Field, ValidationError
from wtforms.validators import InputRequired
from app import constants

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]  # Default validator
        super().__init__(label=label, validators=validators, **kwargs)

    def validate(self, value):
        try:
            datetime.strptime(value, self.format)
        except ValueError:
            raise ValidationError(constants.INVALID_DATETIME_FORMAT)
from wtforms import Field
from wtforms.validators import InputRequired

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]  # Default validator
        super().__init__(label=label, validators=validators, **kwargs)

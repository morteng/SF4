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
from wtforms import Field
from wtforms.validators import InputRequired

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]  # Default validator
        super().__init__(label=label, validators=validators, **kwargs)
from wtforms import Field
from wtforms.validators import InputRequired

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]  # Default validator
        super().__init__(label=label, validators=validators, **kwargs)
from wtforms import Field
from wtforms.validators import InputRequired

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]  # Default validator
        super().__init__(label=label, validators=validators, **kwargs)
from wtforms import Field
from wtforms.validators import InputRequired

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]  # Default validator
        super().__init__(label=label, validators=validators, **kwargs)
from wtforms import Field
from wtforms.validators import InputRequired
from datetime import datetime
from wtforms import ValidationError
from app.constants import MISSING_REQUIRED_FIELD, INVALID_DATETIME_FORMAT

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, format="%Y-%m-%d %H:%M:%S", **kwargs):
        if validators is None:
            validators = [InputRequired(message=MISSING_REQUIRED_FIELD)]
        self.format = format
        super().__init__(label=label, validators=validators, **kwargs)

    def process_formdata(self, valuelist):
        if not valuelist or not valuelist[0].strip():
            self.data = None
            return
            
        date_str = valuelist[0]
        try:
            self.data = datetime.strptime(date_str, self.format)
        except ValueError:
            raise ValidationError(INVALID_DATETIME_FORMAT)

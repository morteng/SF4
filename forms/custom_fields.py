from wtforms import Field
from wtforms.validators import InputRequired

class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]  # Default validator
        super().__init__(label=label, validators=validators, **kwargs)

from datetime import datetime
from wtforms import Field, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Regexp, Optional
from app.constants import FlashMessages

class StipendNameField(StringField):
    """Custom field for validating stipend names."""
    
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [
                InputRequired(message=FlashMessages.NAME_REQUIRED),
                Length(max=100, message=FlashMessages.NAME_LENGTH),
                Regexp(r'^[a-zA-Z0-9\s\-.,!?\'"()]+$', 
                      message=FlashMessages.INVALID_NAME_CHARACTERS)
            ]
        super().__init__(label=label, validators=validators, **kwargs)

class OptionalStringField(StringField):
    """Custom field that allows empty strings."""
    
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [
                Optional(),
                Length(max=255, message=FlashMessages.FIELD_TOO_LONG)
            ]
        super().__init__(label=label, validators=validators, **kwargs)

class OptionalTextAreaField(TextAreaField):
    """Custom text area field that allows empty strings."""
    
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [
                Optional(),
                Length(max=2000, message=FlashMessages.FIELD_TOO_LONG)
            ]
        super().__init__(label=label, validators=validators, **kwargs)

class OptionalStringField(StringField):
    """Custom field that allows empty strings."""
    
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [
                Optional(),
                Length(max=255, message=FlashMessages.FIELD_TOO_LONG)
            ]
        super().__init__(label=label, validators=validators, **kwargs)


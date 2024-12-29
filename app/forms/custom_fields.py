from wtforms import Field
from wtforms.validators import InputRequired
from datetime import datetime
from wtforms import ValidationError
from app.constants import MISSING_REQUIRED_FIELD, INVALID_DATETIME_FORMAT

class CustomDateTimeField(Field):
    """Custom datetime field that validates and parses datetime strings.
    
    Attributes:
        format (str): The datetime format string (default: '%Y-%m-%d %H:%M:%S')
    """
    
    def __init__(self, label=None, validators=None, format="%Y-%m-%d %H:%M:%S", **kwargs):
        """Initialize the datetime field."""
        # Remove format from kwargs if it exists to avoid duplicate parameter
        kwargs.pop('format', None)
        
        # Initialize the field with validators
        self.format = format
        super().__init__(label=label, validators=validators, **kwargs)

    def process_formdata(self, valuelist):
        """Process form data into a datetime object.
        
        Args:
            valuelist (list): List of values from form submission
            
        Raises:
            ValidationError: If the datetime format is invalid
        """
        if not valuelist or not valuelist[0].strip():
            self.data = None
            return
            
        date_str = valuelist[0]
        try:
            self.data = datetime.strptime(date_str, self.format)
        except ValueError:
            raise ValidationError(INVALID_DATETIME_FORMAT)

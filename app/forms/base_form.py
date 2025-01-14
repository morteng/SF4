from flask_wtf import FlaskForm
from wtforms import Field, ValidationError
from app.constants import FlashMessages

class BaseForm(FlaskForm):
    """Base form class with common functionality"""
    
    def validate(self):
        # Add any base validation logic here
        return super().validate()

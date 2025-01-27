from flask_wtf import FlaskForm
from wtforms import SubmitField

class BaseForm(FlaskForm):
    """Base form class with common functionality"""
    
    def validate(self):
        # Add any base validation logic here
        return super().validate()

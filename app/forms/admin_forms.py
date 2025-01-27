"""Forms for admin-related functionality"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField
)
from wtforms.validators import DataRequired

class StipendForm(FlaskForm):
    """Form for creating and editing stipends"""
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')

"""Forms for admin-related functionality"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, URLField, SubmitField
)
from wtforms.validators import DataRequired, Length, URL

class OrganizationForm(FlaskForm):
    """Form for creating and editing organizations"""
    name = StringField('Name', validators=[
        DataRequired(),
        Length(max=100)
    ])
    description = TextAreaField('Description')
    homepage_url = URLField('Website', validators=[
        DataRequired(),
        URL()
    ])
    submit = SubmitField('Create')

class StipendForm(FlaskForm):
    """Form for creating and editing stipends"""
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')

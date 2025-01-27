"""Forms for admin-related functionality"""

from flask_wtf import FlaskForm
from wtforms import (
    HiddenField, SelectField, SelectMultipleField, SubmitField,
    StringField, TextAreaField, URLField
)
from wtforms.validators import DataRequired, Length, URL
from app.models.organization import Organization
from app.models.tag import Tag
from app.extensions import db

class TagForm(FlaskForm):
    """Form for handling tag selections"""
    organization_id = SelectField('Organization', coerce=int)
    tags = SelectMultipleField('Tags')
    submit = SubmitField('Update')

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

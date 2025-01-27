"""Forms for admin-related functionality"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, URLField, SubmitField,
    SelectField, SelectMultipleField
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
        DataRequired(message="Organization name is required"),
        Length(min=2, max=100, message="Name must be between 2-100 characters")
    ])
    description = TextAreaField('Description')
    homepage_url = URLField('Website', validators=[
        DataRequired(message="Website URL is required"),
        URL(require_tld=True, message="Invalid URL format")
    ])
    submit = SubmitField('Save Organization')

class StipendForm(FlaskForm):
    """Form for creating and editing stipends"""
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')

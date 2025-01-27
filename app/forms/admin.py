"""Forms for admin-related functionality"""

from flask_wtf import FlaskForm
from wtforms import (
    HiddenField, SelectField, SelectMultipleField, SubmitField
)
from app.models.organization import Organization
from app.models.tag import Tag
from app.extensions import db

class TagForm(FlaskForm):
    """Form for handling tag selections"""
    organization_id = SelectField('Organization', coerce=int)
    tags = SelectMultipleField('Tags')
    submit = SubmitField('Update')

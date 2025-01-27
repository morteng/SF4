"""Forms for admin-related functionality"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, URLField, SubmitField,
    HiddenField, SelectField, SelectMultipleField
)
from wtforms.validators import DataRequired, Length, URL
from app.models.organization import Organization
from app.models.tag import Tag
from app.extensions import db

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization_id.choices = [
            (org.id, org.name) for org in Organization.query.order_by(Organization.name).all()
        ]
        self.tags.choices = [
            (tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()
        ]

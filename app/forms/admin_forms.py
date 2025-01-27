"""Forms for admin-related functionality"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, URLField, SubmitField
)
from wtforms.validators import DataRequired, Length, URL

# OrganizationForm has been moved to admin.py

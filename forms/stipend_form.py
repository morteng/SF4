from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
from .custom_fields import CustomDateTimeField

class StipendForm(FlaskForm):
    application_deadline = CustomDateTimeField(
        "Application Deadline",
        format="%Y-%m-%d %H:%M:%S",
        validators=[InputRequired()]  # Explicitly pass validators
    )

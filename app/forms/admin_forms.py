from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from datetime import datetime

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    summary = TextAreaField('Summary', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    homepage_url = URLField('Homepage URL', validators=[Optional()])
    application_procedure = TextAreaField('Application Procedure', validators=[Optional()])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[Optional()])
    application_deadline = DateTimeField('Application Deadline', format='%Y-%m-%d %H:%M:%S', validators=[Optional(), validate_application_deadline])
    open_for_applications = BooleanField('Open for Applications')

def validate_application_deadline(form, field):
    if field.data:
        try:
            datetime.strptime(field.data, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValidationError(f"Invalid date format. Please use YYYY-MM-DD HH:MM:SS.")

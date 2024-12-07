from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, DateTimeField, SubmitField
from wtforms.validators import Length, ValidationError
from datetime import datetime

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=255)])
    summary = TextAreaField('Summary')
    description = TextAreaField('Description')
    homepage_url = URLField('Homepage URL')
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = DateTimeField('Application Deadline', format='%Y-%m-%d %H:%M:%S')  # Removed DataRequired()
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

    def validate_application_deadline(self, field):
        if field.data:
            try:
                # Ensure the data is a string before parsing
                if isinstance(field.data, datetime):
                    field.data = field.data.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    datetime.strptime(field.data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValidationError('Not a valid datetime value. Please use the format YYYY-MM-DD HH:MM:SS.')
        else:
            field.data = None  # Set to None if the field is empty

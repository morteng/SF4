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
                field.data = None  # Set to None if the data is not a valid datetime
        else:
            field.data = None  # Set to None if the field is empty

class BotForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=255)])
    description = TextAreaField('Description')
    status = StringField('Status')
    submit = SubmitField('Create')

    def validate_status(self, field):
        if field.data not in ['active', 'inactive']:
            raise ValidationError('Status must be either "active" or "inactive".')

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=255)])
    description = TextAreaField('Description')
    homepage_url = URLField('Homepage URL')
    submit = SubmitField('Create')

class TagForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=255)])
    category = StringField('Category')
    submit = SubmitField('Create')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[Length(max=255)])
    email = StringField('Email')
    password = StringField('Password')
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Create')

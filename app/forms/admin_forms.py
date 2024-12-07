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
    application_deadline = DateTimeField('Application Deadline', format='%Y-%m-%d %H:%M:%S')
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

    def validate_application_deadline(self, field):
        if field.data:
            try:
                datetime.strptime(field.data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValidationError('Not a valid datetime value. Please use the format YYYY-MM-DD HH:MM:SS.')

class BotForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=255)])
    description = TextAreaField('Description')
    status = StringField('Status')
    submit = SubmitField('Save')

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=255)])
    description = TextAreaField('Description')
    homepage_url = URLField('Homepage URL')
    submit = SubmitField('Save')

class TagForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=255)])
    category = StringField('Category')
    submit = SubmitField('Save')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[Length(max=255)])
    email = StringField('Email', validators=[Length(max=255)])
    password = StringField('Password')
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Save')

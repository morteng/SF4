from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    summary = TextAreaField('Summary')
    description = TextAreaField('Description')
    homepage_url = URLField('Homepage URL')
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = DateTimeField('Application Deadline', format='%Y-%m-%d %H:%M:%S')
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

class BotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description')
    status = StringField('Status', validators=[DataRequired()])
    submit = SubmitField('Save')

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description')
    homepage_url = URLField('Homepage URL')
    submit = SubmitField('Save')

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    category = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Save')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Length(max=255)])
    password = StringField('Password', validators=[DataRequired()])
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Save')

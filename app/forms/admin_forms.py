from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=255)])
    homepage_url = StringField('Homepage URL', validators=[Length(max=255)])
    submit = SubmitField('Create')

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    summary = TextAreaField('Summary', validators=[Length(max=255)])
    description = TextAreaField('Description')
    homepage_url = StringField('Homepage URL', validators=[Length(max=255)])
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = StringField('Application Deadline')
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    category = StringField('Category', validators=[Length(max=50)])
    submit = SubmitField('Create')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=8)])
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Create')

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Email, Optional
from app.models.stipend import Stipend
from datetime import datetime

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
    # Change this to StringField
    application_deadline = StringField(
        'Application Deadline', 
        validators=[Optional(), Length(max=100)]
    )
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

    def validate_name(self, name):
        stipend = Stipend.query.filter_by(name=name.data).first()
        if stipend:
            raise ValidationError('Stipend with this name already exists.')

    def validate_application_deadline(self, field):
        data = field.data
        # If it's empty or just whitespace, set None
        if not data or not data.strip():
            field.data = None
            return

        # If there's something in the field, try parsing it
        try:
            # Just try parsing to see if it's valid, but we won't store datetime directly
            datetime.strptime(data.strip(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            # If it's invalid, just store None
            field.data = None

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

class BotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=255)])
    submit = SubmitField('Submit')

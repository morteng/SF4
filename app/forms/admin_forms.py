from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.forms.fields import CustomDateTimeField
from datetime import datetime  # Ensure this is imported
from app.models.tag import Tag  # Import the Tag model
from app.models.user import User  # Import the User model
from app.models.bot import Bot  # Import the Bot model
from app.models.organization import Organization  # Import the Organization model

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    summary = TextAreaField('Summary', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    homepage_url = URLField('Homepage URL', validators=[Optional()])
    application_procedure = TextAreaField('Application Procedure', validators=[Optional()])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[Optional()])
    application_deadline = CustomDateTimeField(
        'Application Deadline',
        format='%Y-%m-%d %H:%M:%S',
        validators=[Optional()]
    )
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            tag = Tag.query.filter_by(name=name.data).first()
            if tag:
                raise ValidationError('Tag with this name already exists.')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Length(max=255)])
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Create')

    def __init__(self, original_username=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('User with this username already exists.')

class BotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    status = StringField('Status', validators=[Length(max=255)])
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(BotForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            bot = Bot.query.filter_by(name=name.data).first()
            if bot:
                raise ValidationError('Bot with this name already exists.')

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            organization = Organization.query.filter_by(name=name.data).first()
            if organization:
                raise ValidationError('Organization with this name already exists.')

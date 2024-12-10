from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.stipend import Stipend
from app.models.tag import Tag
from app.models.user import User
from app.models.bot import Bot
from app.models.organization import Organization
from datetime import datetime

class NullableDateTimeField(StringField):
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0].strip():
            try:
                self.data = datetime.strptime(valuelist[0], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.data = None
        else:
            self.data = None

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    summary = TextAreaField('Summary')  # Ensure this field is present and not restricted
    description = TextAreaField('Description')
    homepage_url = URLField('Homepage URL', validators=[Length(max=255)])
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = NullableDateTimeField('Application Deadline (YYYY-MM-DD HH:MM:SS)')  # Use the custom field
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(StipendForm, self).__init__(*args, **kwargs)
        if original_name:
            self.name.data = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            stipend = Stipend.query.filter_by(name=name.data).first()
            if stipend:
                raise ValidationError('Stipend with this name already exists.')

class StipendEditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    summary = StringField('Summary', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    homepage_url = URLField('Homepage URL')
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = NullableDateTimeField('Application Deadline (YYYY-MM-DD HH:MM:SS)')  # Use the custom field
    open_for_applications = BooleanField('Open for Applications')

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

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, Email, URL, Regexp  # Add URL and Regexp here
from app.models.organization import Organization
from app.forms.fields import CustomDateTimeField
from app.models.tag import Tag
from app.models.user import User
from app.models.bot import Bot

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    summary = TextAreaField('Summary', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    homepage_url = URLField('Homepage URL', validators=[Optional(), URL()])  # Add URL validator here
    application_procedure = TextAreaField('Application Procedure', validators=[Optional()])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[Optional()])
    application_deadline = CustomDateTimeField(
        'Application Deadline',
        format='%Y-%m-%d %H:%M:%S',
        validators=[Optional()]
    )
    open_for_applications = BooleanField('Open for Applications', default=False)
    submit = SubmitField('Create')

    def validate_application_deadline(self, field):
        if field.raw_data and field.raw_data[0] and field.data is None:
            raise ValidationError('Invalid date format. Please use YYYY-MM-DD HH:MM:SS.')

    def validate_name(self, name):
        if not name.data:
            raise ValidationError('This field is required.')

    def process_data(self, data):
        super().process_data(data)
        if 'open_for_applications' in data:
            if data['open_for_applications'] == '0':
                self.open_for_applications.data = False
            elif data['open_for_applications'] == '1':
                self.open_for_applications.data = True
            else:
                self.open_for_applications.data = bool(data['open_for_applications'])

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    category = StringField('Category', validators=[DataRequired(), Length(max=100)])  # Keep only one
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if not name.data:
            raise ValidationError('Name cannot be empty.')
        if self.original_name and name.data == self.original_name:
            return  # Skip validation if the name hasn't changed
        tag = Tag.query.filter_by(name=name.data).first()
        if tag:
            raise ValidationError('Tag with this name already exists.')

    def validate_category(self, category):
        if not category.data:
            raise ValidationError('Category cannot be empty.')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[Optional()])
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Create')

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

from wtforms.validators import InputRequired

class BotForm(FlaskForm):

    name = StringField('Name', validators=[InputRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[InputRequired(), Length(max=500)])
    status = BooleanField('Status', default=False)
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(BotForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            bot = Bot.query.filter_by(name=name.data).first()
            if bot:
                raise ValidationError('Bot with this name already exists.')
    
    def validate_status(self, field):
        if field.raw_data:
            value = field.raw_data[0].lower()
            if value in ['true', '1', 'y', 'yes', 'on']:
                field.data = True
            elif value in ['false', '0', 'n', 'no', 'off']:
                field.data = False
            else:
                raise ValidationError("Invalid value for status. It must be true or false.")

class OrganizationForm(FlaskForm):
    name = StringField('Org Name', validators=[
        DataRequired(),
        Length(max=100),
        Regexp('^[A-Za-z0-9 ]*$', message='Name must contain only letters, numbers, and spaces.')
    ])
    description = TextAreaField('About')
    homepage_url = URLField('Website', validators=[Optional(), URL()])  # URL validator remains
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.original_name = original_name or None

    def validate_name(self, name):
        if name.data != self.original_name:
            organization = Organization.query.filter_by(name=name.data).first()
            if organization:
                raise ValidationError('Organization with this name already exists.')

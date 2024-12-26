from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, SubmitField, PasswordField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, Email, URL, Regexp  # Add URL and Regexp here
from app.models.organization import Organization
from app.forms.fields import CustomDateTimeField
from app.models.tag import Tag
from app.models.user import User
from app.models.bot import Bot


class StipendForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message="Name is required."),
        Length(max=100, message="Name cannot exceed 100 characters.")
    ])
    summary = TextAreaField('Summary', validators=[
        Optional(),
        Length(max=500, message="Summary cannot exceed 500 characters.")
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=2000, message="Description cannot exceed 2000 characters.")
    ])
    homepage_url = URLField('Homepage URL', validators=[
        Optional(),
        URL(message="Please enter a valid URL starting with http:// or https://.")
    ])
    application_procedure = TextAreaField('Application Procedure', validators=[
        Optional(),
        Length(max=1000, message="Application procedure cannot exceed 1000 characters.")
    ])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[
        Optional(),
        Length(max=1000, message="Eligibility criteria cannot exceed 1000 characters.")
    ])
    application_deadline = CustomDateTimeField(
        'Application Deadline',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M:%S'
    )
    organization_id = SelectField('Organization', validators=[DataRequired(message="Organization is required.")], coerce=int, choices=[])
    open_for_applications = BooleanField('Open for Applications', default=False)
    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure organization choices are always populated
        self.organization_id.choices = [(org.id, org.name) for org in Organization.query.order_by(Organization.name).all()]
        if not self.organization_id.data and self.organization_id.choices:
            self.organization_id.data = self.organization_id.choices[0][0]

    def validate_application_deadline(self, field):
        if field.data and field.data < datetime.now():
            raise ValidationError('Application deadline cannot be in the past.')

    def validate_open_for_applications(self, field):
        if field.data is None:
            field.data = False
        elif isinstance(field.data, str):
            field.data = field.data.lower() in ['y', 'yes', 'true', '1']
        elif not isinstance(field.data, bool):
            field.data = False

    def validate_summary(self, field):
        if field.data and field.data.strip() == '':
            raise ValidationError('Summary cannot be just whitespace.')

    def validate_description(self, field):
        if field.data and field.data.strip() == '':
            raise ValidationError('Description cannot be just whitespace.')

    def validate_organization_id(self, field):
        if not field.data:
            raise ValidationError('Organization is required.')
        organization = Organization.query.get(field.data)
        if not organization:
            raise ValidationError('Invalid organization selected.')

    def validate_summary(self, field):
        if field.data and field.data.strip() == '':
            raise ValidationError('Summary cannot be just whitespace.')

    def validate_description(self, field):
        if field.data and field.data.strip() == '':
            raise ValidationError('Description cannot be just whitespace.')


class TagForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message="Name is required."),
        Length(max=100, message="Name cannot exceed 100 characters.")
    ])
    category = StringField('Category', validators=[
        DataRequired(message="Category is required."),
        Length(max=100, message="Category cannot exceed 100 characters.")
    ])
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if self.original_name and name.data == self.original_name:
            return  # Skip validation if the name hasn't changed
        tag = Tag.query.filter_by(name=name.data).first()
        if tag:
            raise ValidationError('Tag with this name already exists.')


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[
        Optional(),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
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


class BotForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required."),
        Length(max=500, message="Description cannot exceed 500 characters.")
    ])
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

    def validate_homepage_url(self, field):
        if field.data and not (field.data.startswith('http://') or field.data.startswith('https://')):
            raise ValidationError('URL must start with http:// or https://.')

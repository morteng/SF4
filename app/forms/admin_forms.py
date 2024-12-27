import pytz
import logging
from datetime import datetime
from flask_wtf import FlaskForm
from app.constants import FlashMessages
from app.forms.fields import CustomDateTimeField
from wtforms.validators import ValidationError
import logging
from wtforms import (
    StringField, TextAreaField, URLField, BooleanField, 
    SubmitField, SelectField, PasswordField, SelectMultipleField
)

# Configure logging
logger = logging.getLogger(__name__)
from wtforms.validators import (
    DataRequired, Length, Optional, ValidationError, 
    URL, Email, Regexp
)
from wtforms.fields import DateTimeField
from app.models.organization import Organization
from app.models.tag import Tag
from app.models.user import User
from app.models.bot import Bot
from app.extensions import db


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
        render_kw={
            "placeholder": "YYYY-MM-DD HH:MM:SS",
            "pattern": r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
            "title": "Please enter date in YYYY-MM-DD HH:MM:SS format."
        },
        error_messages={
            'invalid_format': 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS',
            'invalid_date': 'Invalid date values (e.g., Feb 30)',
            'invalid_time': 'Invalid time values (e.g., 25:61:61)',
            'missing_time': 'Time is required. Please use YYYY-MM-DD HH:MM:SS',
            'required': 'Date is required',
            'invalid_leap_year': 'Invalid date values (e.g., Feb 29 in non-leap years)'
        }
    )
    organization_id = SelectField('Organization', coerce=int, validators=[Optional()])
    open_for_applications = BooleanField('Open for Applications', default=False)
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])

    def validate_application_deadline(self, field):
        # Skip validation if the field is empty or invalid (CustomDateTimeField handles this)
        if not field.data or field.errors:
            print(f"Field data: {field.data}, Errors: {field.errors}")  # Debugging
            return
        
        # If we somehow still have a string, convert it to datetime
        if isinstance(field.data, str):
            try:
                field.data = datetime.strptime(field.data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValidationError('Invalid date format')
    
        # Ensure datetime is timezone-aware
        now = datetime.now(pytz.UTC)
        if field.data.tzinfo is None:
            field.data = pytz.UTC.localize(field.data)
        
        # Validate future date
        if field.data < now:
            raise ValidationError('Application deadline must be a future date')
        
        # Validate not too far in future
        max_future = now.replace(year=now.year + 5)
        if field.data > max_future:
            raise ValidationError('Application deadline cannot be more than 5 years in the future')

    organization_id = SelectField('Organization', validators=[DataRequired(message="Organization is required.")], coerce=int, choices=[])
    open_for_applications = BooleanField('Open for Applications', default=False)
    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure organization choices are always populated
        self.organization_id.choices = [(org.id, org.name) for org in Organization.query.order_by(Organization.name).all()]
        if not self.organization_id.data and self.organization_id.choices:
            self.organization_id.data = self.organization_id.choices[0][0]


    def validate_open_for_applications(self, field):
        # Handle string values from form submission
        if isinstance(field.data, str):
            field.data = field.data.lower() in ['true', 'yes', '1', 'y', 'on']
        # Convert None to False
        elif field.data is None:
            field.data = False
        # Ensure the field data is properly set in the form
        self.open_for_applications.data = field.data
        return None  # Explicitly return None as required by WTForms

    def validate_organization_id(self, field):
        if not field.data:
            raise ValidationError('Organization is required.')
        organization = db.session.get(Organization, field.data)  # Updated to use db.session.get
        if not organization:
            raise ValidationError('Invalid organization selected.')


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

    def validate_name(self, name: StringField) -> None:
        """
        Validate the organization name field.
        
        Args:
            name: The name field to validate
            
        Raises:
            ValidationError: If the name is invalid
        """
        if self.original_name and name.data == self.original_name:
            return  # Skip validation if the name hasn't changed
        tag = Tag.query.filter_by(name=name.data).first()
        if tag:
            raise ValidationError('Tag with this name already exists.')


from wtforms import HiddenField

class UserForm(FlaskForm):
    id = HiddenField('ID')
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50),
        Regexp('^[a-zA-Z0-9_]+$', message="Username can only contain letters, numbers and underscores")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=255)
    ])
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
            user = db.session.get(User, username.data)
            if user is not None:
                raise ValidationError(FlashMessages.FORM_DUPLICATE_USERNAME.value)

    def validate_email(self, email):
        if email.data != self.original_email:
            user = db.session.get(User, email.data)
            if user is not None:
                raise ValidationError(FlashMessages.FORM_DUPLICATE_EMAIL.value)


class BotForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message="Name is required."),
        Length(max=100, message="Name cannot exceed 100 characters."),
        Regexp('^[A-Za-z0-9 ]*$', message='Name must contain only letters, numbers, and spaces.')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required."),
        Length(max=500, message="Description cannot exceed 500 characters.")
    ])
    status = BooleanField('Status', default=False)
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(BotForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, field):
        if not field.data or field.data.strip() == '':
            raise ValidationError('Name is required.')
        if field.data != self.original_name:
            bot = Bot.query.filter_by(name=field.data).first()
            if bot:
                raise ValidationError('Bot with this name already exists.')

    def validate_status(self, field):
        if isinstance(field.data, str):
            if field.data.lower() not in ['true', 'false', 'yes', 'no', '1', '0', 'y', 'n', 'on', 'off']:
                raise ValidationError('Invalid status value')
            field.data = field.data.lower() in ['true', 'yes', '1', 'y', 'on']
        elif field.data is None:
            field.data = False


class OrganizationForm(FlaskForm):
    id = HiddenField('ID')
    csrf_token = HiddenField('CSRF Token')
    name = StringField('Name', validators=[
        DataRequired(message="This field is required."),
        Length(max=100, message="Organization name cannot exceed 100 characters."),
        Regexp('^[A-Za-z0-9 ]*$', message='Organization name must contain only letters, numbers, and spaces.')
    ])
    description = TextAreaField('About', validators=[
        Length(max=500, message="Description cannot exceed 500 characters.")
    ], render_kw={"maxlength": 500, "data-maxlength": "500"})
    homepage_url = URLField('Website', validators=[
        DataRequired(message="Website URL is required."),
        URL(message="Please enter a valid URL starting with http:// or https://.")
    ])
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.original_name = original_name or None

    def validate_name(self, name):
        if not name.data or not name.data.strip():
            raise ValidationError('Name: This field is required.')
        if len(name.data.strip()) > 100:
            raise ValidationError('Name: Organization name cannot exceed 100 characters.')
        if name.data != self.original_name:
            try:
                organization = Organization.query.filter_by(name=name.data).first()
                if organization:
                    logger.warning(f"Duplicate organization name detected: {name.data}")
                    raise ValidationError('Name: Organization with this name already exists.')
            except Exception as e:
                logger.error(f"Error validating organization name: {str(e)}")
                raise ValidationError('Failed to validate organization name: ' + str(e))

    def validate_homepage_url(self, field):
        if field.data and not (field.data.startswith('http://') or field.data.startswith('https://')):
            raise ValidationError('URL must start with http:// or https://.')

    def validate_description(self, field):
        """Custom validation for description field"""
        # Skip validation if field is empty
        if not field.data:
            return
            
        # Ensure the description is a string
        if not isinstance(field.data, str):
            raise ValidationError('Description must be a string')
            
        # Strip whitespace and check length
        stripped = field.data.strip()
        if len(stripped) > 500:
            raise ValidationError('Description cannot exceed 500 characters')
        
        # Update the field data with stripped value
        field.data = stripped

import re
import pytz
import logging
from datetime import datetime
from flask_wtf import FlaskForm
from app.constants import FlashMessages
from app.forms.custom_fields import CustomDateTimeField
from app.common.utils import validate_application_deadline
from wtforms.validators import ValidationError
import logging
from wtforms import (
    StringField, TextAreaField, URLField, BooleanField, 
    SubmitField, SelectField, PasswordField, SelectMultipleField,
    HiddenField
)
from wtforms.validators import (
    DataRequired, Length, Optional, ValidationError, 
    URL, Email, Regexp, InputRequired
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
    def __init__(self, *args, **kwargs):
        logger.debug("Initializing StipendForm")
        super().__init__(*args, **kwargs)
        logger.debug(f"Form fields initialized: {self._fields.keys()}")
        
    csrf_token = HiddenField('CSRF Token', validators=[
        DataRequired(message="CSRF token is required")
    ])
    name = StringField('Name', validators=[
        DataRequired(message=FlashMessages.NAME_REQUIRED),
        Length(max=100, message=FlashMessages.NAME_LENGTH),
        Regexp(r'^[a-zA-Z0-9\s\-,.()\'"]+$', 
               message=FlashMessages.INVALID_NAME_CHARACTERS)
    ])
    summary = TextAreaField('Summary', validators=[
        DataRequired(message=FlashMessages.MISSING_FIELD_ERROR.value),
        Length(max=500, message="Summary cannot exceed 500 characters.")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message=FlashMessages.MISSING_FIELD_ERROR.value),
        Length(max=2000, message="Description cannot exceed 2000 characters.")
    ])
    homepage_url = URLField('Homepage URL', validators=[
        DataRequired(message=FlashMessages.MISSING_FIELD_ERROR.value),
        URL(message=FlashMessages.INVALID_URL.value)
    ])
    application_procedure = TextAreaField('Application Procedure', validators=[
        DataRequired(message=FlashMessages.MISSING_FIELD_ERROR.value),
        Length(max=2000, message="Application procedure cannot exceed 2000 characters.")
    ])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[
        DataRequired(message=FlashMessages.MISSING_FIELD_ERROR.value),
        Length(max=2000, message="Eligibility criteria cannot exceed 2000 characters.")
    ])
    application_deadline = CustomDateTimeField(
        'Application Deadline',
        format="%Y-%m-%d %H:%M:%S",
        validators=[
            InputRequired(message=FlashMessages.MISSING_FIELD_ERROR),
            validate_application_deadline
        ]
    )
    organization_id = SelectField('Organization', coerce=int, validators=[
        DataRequired(message="Organization is required.")
    ])
    open_for_applications = BooleanField('Open for Applications', default=False)
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])

    def validate_application_deadline(self, field):
        validate_application_deadline(field)

    def validate_organization_id(self, field):
        if field.data:  # Only validate if organization_id is provided
            organization = db.session.get(Organization, field.data)
            if not organization:
                raise ValidationError('Invalid organization selected.')

    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize organization choices
        self.organization_id.choices = [
            (org.id, org.name) for org in Organization.query.order_by(Organization.name).all()
        ]
        
        # Initialize tag choices
        self.tags.choices = [
            (tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()
        ]
        
        # Set default values for existing stipend
        if kwargs.get('obj'):
            self.tags.data = [tag.id for tag in kwargs['obj'].tags]
            self.organization_id.data = kwargs['obj'].organization_id


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
        if field.data:  # Only validate if organization_id is provided
            organization = db.session.get(Organization, field.data)
            if not organization:
                raise ValidationError('Invalid organization selected.')

    def validate(self):
        logger.debug("Validating StipendForm")
        
        # Add validation for required relationships
        if not self.organization_id.data:
            self.organization_id.errors.append("Organization is required")
            return False
            
        # Validate tags
        if not self.tags.data:
            self.tags.errors.append("At least one tag is required")
            return False
            
        # Additional custom validation
        if self.application_deadline.data and self.application_deadline.data < datetime.now():
            self.application_deadline.errors.append("Deadline must be in the future")
            return False
            
        return super().validate()


class TagForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message=FlashMessages.NAME_REQUIRED.value),
        Length(max=100, message=FlashMessages.NAME_LENGTH.value)
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


from flask_login import current_user
from wtforms import HiddenField

class UserForm(FlaskForm):
    id = HiddenField('ID')
    username = StringField('Username', validators=[
        DataRequired(message=FlashMessages.USERNAME_REQUIRED.value),
        Length(min=3, max=50, message=FlashMessages.USERNAME_LENGTH.value),
        Regexp('^[a-zA-Z0-9_]+$', message=FlashMessages.USERNAME_FORMAT.value)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=255)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    is_admin = BooleanField('Is Admin')
    is_active = BooleanField('Is Active', default=True)
    created_at = DateTimeField('Created At', format='%Y-%m-%d %H:%M:%S', render_kw={'readonly': True})
    updated_at = DateTimeField('Updated At', format='%Y-%m-%d %H:%M:%S', render_kw={'readonly': True})
    submit = SubmitField('Save')

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        # Remove password field for existing users
        if kwargs.get('obj'):
            del self.password

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError(FlashMessages.USERNAME_ALREADY_EXISTS.value)

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
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
        DataRequired(message=FlashMessages.NAME_REQUIRED),
        Length(max=100, message=FlashMessages.NAME_LENGTH),
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
        """Enhanced name validation with better error messages"""
        if not name.data or not name.data.strip():
            raise ValidationError(FlashMessages.NAME_REQUIRED.value)
            
        if len(name.data) > 100:
            raise ValidationError(FlashMessages.NAME_LENGTH.value)
            
        if not re.match(r'^[a-zA-Z0-9\s\-,.()\'"]+$', name.data):
            logger.warning(f"Invalid characters in organization name: {name.data}")
            raise ValidationError(FlashMessages.INVALID_NAME_CHARACTERS.value)
            try:
                organization = Organization.query.filter_by(name=name.data).first()
                if organization:
                    # Create notification for duplicate name attempt
                    from app.models.notification import Notification
                    notification = Notification(
                        message=f"Duplicate organization name attempt: {name.data}",
                        type="user_action",
                        read_status=False
                    )
                    db.session.add(notification)
                    
                    # Create audit log
                    from app.models.audit_log import AuditLog
                    AuditLog.create(
                        user_id=current_user.id if current_user.is_authenticated else 0,
                        action="duplicate_org_attempt",
                        details=f"Attempt to create duplicate organization: {name.data}",
                        object_type="Organization",
                        object_id=organization.id if organization else None
                    )
                    
                    logger.warning(f"Duplicate organization name detected: {name.data}")
                    raise ValidationError('Name: Organization with this name already exists.')
            except Exception as e:
                # Log error and create notification
                logger.error(f"Error validating organization name: {str(e)}")
                notification = Notification(
                    message=f"Error validating organization name: {str(e)}",
                    type="system",
                    read_status=False
                )
                db.session.add(notification)
                
                # Create audit log for error
                from app.models.audit_log import AuditLog
                AuditLog.create(
                    user_id=current_user.id if current_user.is_authenticated else 0,
                    action="validation_error",
                    details=f"Error validating organization name: {str(e)}",
                    object_type="Organization",
                    object_id=None
                )
                
                db.session.commit()
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

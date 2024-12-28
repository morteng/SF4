import logging
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from app.models.user import User
from app.utils import generate_csrf_token
from app.constants import FlashMessages

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message=FlashMessages.USERNAME_REQUIRED.value),
        Length(min=3, max=50, message=FlashMessages.USERNAME_LENGTH.value)
    ])
    email = StringField('Email', validators=[
        DataRequired(message=FlashMessages.EMAIL_REQUIRED.value),
        Email(message=FlashMessages.EMAIL_INVALID.value),
        Length(max=100, message=FlashMessages.EMAIL_LENGTH.value)
    ])
    csrf_token = HiddenField('CSRF Token')
    submit = SubmitField('Save Changes')

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user and user.id != current_user.id:
                raise ValidationError(FlashMessages.USERNAME_ALREADY_EXISTS.value)

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user and (not hasattr(current_user, 'id') or user.id != current_user.id):
                raise ValidationError(FlashMessages.EMAIL_ALREADY_EXISTS.value)

    def validate_csrf_token(self, field):
        """Custom CSRF token validation with enhanced error handling."""
        logger = logging.getLogger(__name__)
        if not field.data:
            logger.warning("Missing CSRF token in profile form")
            raise ValidationError(FlashMessages.CSRF_INVALID.value)
        try:
            from flask_wtf.csrf import validate_csrf
            validate_csrf(field.data)
        except Exception as e:
            logger.error(f"CSRF validation failed: {str(e)}")
            raise ValidationError(FlashMessages.CSRF_INVALID.value)

    def __init__(self, original_username, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        # Initialize CSRF token
        self.csrf_token.data = generate_csrf_token()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username: StringField) -> None:
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(FlashMessages.USERNAME_ALREADY_EXISTS)

    def validate_email(self, email: StringField) -> None:
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(FlashMessages.EMAIL_ALREADY_EXISTS)

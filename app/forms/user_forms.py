from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
import logging

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger(__name__)
from flask import session
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from app.models.user import User
from app.constants import FlashMessages, FlashCategory  # Import FlashMessages and FlashCategory from constants
from app.utils import flash_message  # Import the flash_message function

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Changes')

    def validate_username(self, username: StringField) -> None:
        try:
            if username.data != self.original_username:
                user = User.query.filter_by(username=username.data).first()
                if user:
                    flash_message(FlashMessages.USERNAME_ALREADY_EXISTS, FlashCategory.ERROR)
                    raise ValidationError(FlashMessages.USERNAME_ALREADY_EXISTS)
        except Exception as e:
            logger.error(f"Error validating username: {e}")
            flash_message(FlashMessages.GENERIC_ERROR, FlashCategory.ERROR)
            raise ValidationError(FlashMessages.GENERIC_ERROR)

    def validate_email(self, email: StringField) -> None:
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                flash_message(FlashMessages.EMAIL_ALREADY_EXISTS, FlashCategory.ERROR)
                raise ValidationError(FlashMessages.EMAIL_ALREADY_EXISTS)

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email


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

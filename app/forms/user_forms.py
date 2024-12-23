from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from flask import session
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from app.models.user import User
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_ERROR  # Import FLASH_MESSAGES and FLASH_CATEGORY_ERROR from constants
from app.utils import flash_message  # Import the flash_message function

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Changes')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate(self, extra_validators=None):
        if not super(ProfileForm, self).validate(extra_validators=extra_validators):
            return False
        user_by_username = User.query.filter_by(username=self.username.data).first()
        if user_by_username is not None and user_by_username.username != self.original_username:
            self.username.errors.append(FLASH_MESSAGES["USERNAME_ALREADY_EXISTS"])
            return False
        user_by_email = User.query.filter_by(email=self.email.data).first()
        if user_by_email is not None and user_by_email.email != self.original_email:
            self.email.errors.append('Please use a different email address.')
            return False
        return True

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

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already exists.')

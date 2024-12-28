from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
from app.models.user import User
from app.utils import generate_csrf_token
from app.constants import FlashMessages

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=50, message="Username must be between 3 and 50 characters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required."),
        Email(message="Invalid email address."),
        Length(max=100, message="Email cannot exceed 100 characters.")
    ])
    csrf_token = HiddenField('CSRF Token')
    submit = SubmitField('Save Changes')

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(FlashMessages.USERNAME_ALREADY_EXISTS.value)

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(FlashMessages.EMAIL_ALREADY_EXISTS.value)

    def validate_csrf_token(self, field):
        """Custom CSRF token validation."""
        if not field.data:
            raise ValidationError(FlashMessages.CSRF_INVALID.value)
        try:
            from flask_wtf.csrf import validate_csrf
            validate_csrf(field.data)
        except Exception:
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

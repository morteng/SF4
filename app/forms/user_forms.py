from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError
from app.models.user import User
from wtforms.validators import DataRequired, Email, EqualTo

class ProfileForm(FlaskForm):
    """Form for updating user profile information."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Changes')

    def __init__(self, original_username, original_email, *args, **kwargs):
        """Initialize the form with the current user's username and email."""
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate(self, extra_validators=None):
        """Validate the form data ensuring unique username and email."""
        if not super(ProfileForm, self).validate(extra_validators=extra_validators):
            return False
        user_by_username = User.query.filter_by(username=self.username.data).first()
        if user_by_username is not None and user_by_username.username != self.original_username:
            self.username.errors.append('Please use a different username.')
            return False
        user_by_email = User.query.filter_by(email=self.email.data).first()
        if user_by_email is not None and user_by_email.email != self.original_email:
            self.email.errors.append('Please use a different email address.')
            return False
        return True

class LoginForm(FlaskForm):
    """Form for logging in a user."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """Form for registering a new user."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

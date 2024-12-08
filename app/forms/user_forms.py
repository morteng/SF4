from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo  # Added EqualTo here
from app.models.user import User

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
            self.username.errors.append('Please use a different username.')
            return False
        user_by_email = User.query.filter_by(email=self.email.data).first()
        if user_by_email is not None and user_by_email.email != self.original_email:
            self.email.errors.append('Please use a different email address.')
            return False
        return True

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    csrf_token = HiddenField()  # Add CSRF token field
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    # Add other fields with validators as needed

class TagForm(FlaskForm):
    # Define fields with validators
    pass

class OrganizationForm(FlaskForm):
    # Define fields with validators
    pass

class UserForm(FlaskForm):
    # Define fields with validators
    pass

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

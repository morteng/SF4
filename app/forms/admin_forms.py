from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    # ... other fields ...

class TagForm(FlaskForm):
    # ... form fields ...
    pass

class OrganizationForm(FlaskForm):
    # ... form fields ...
    pass

class UserForm(FlaskForm):
    # ... form fields ...
    pass

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

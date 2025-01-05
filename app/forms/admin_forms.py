from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    PasswordField, 
    SubmitField, 
    TextAreaField, 
    BooleanField,
    DateField
)
from wtforms.validators import DataRequired, URL

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    summary = StringField('Summary', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    homepage_url = StringField('Homepage URL', validators=[DataRequired(), URL()])
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = DateField('Application Deadline', format='%Y-%m-%d')
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TagForm(FlaskForm):
    # ... form fields and methods ...
    pass

class OrganizationForm(FlaskForm):
    # ... form fields and methods ...
    pass

class UserForm(FlaskForm):
    # ... form fields and methods ...
    pass

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# app/forms/admin_forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, PasswordField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models.user import User
from app.models.tag import Tag

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    summary = StringField('Summary', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    homepage_url = StringField('Homepage URL', validators=[DataRequired()])
    application_procedure = TextAreaField('Application Procedure', validators=[DataRequired()])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[DataRequired()])
    application_deadline = DateField('Application Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    open_for_applications = BooleanField('Open for Applications')
    tags = SelectField('Tags', coerce=int)
    organizations = SelectField('Organizations', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(StipendForm, self).__init__(*args, **kwargs)
        # Populate tag choices
        self.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]
        # Similarly, populate organization choices
        # self.organizations.choices = [...]

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Submit')

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    homepage_url = StringField('Homepage URL', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class BotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

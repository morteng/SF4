from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, DateTimeField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Email
from app.models.stipend import Stipend

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=255)])
    homepage_url = StringField('Homepage URL', validators=[Length(max=255)])
    submit = SubmitField('Create')

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    summary = TextAreaField('Summary', validators=[Length(max=255)])
    description = TextAreaField('Description')
    homepage_url = StringField('Homepage URL', validators=[Length(max=255)])
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = DateTimeField('Application Deadline', format='%Y-%m-%d %H:%M:%S', validators=[])
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

    def validate_name(self, name):
        stipend = Stipend.query.filter_by(name=name.data).first()
        if stipend:
            raise ValidationError('Stipend with this name already exists.')

    def validate_application_deadline(self, application_deadline):
        if self.application_deadline.data is not None and isinstance(self.application_deadline.data, str):
            try:
                from datetime import datetime
                self.application_deadline.data = datetime.strptime(self.application_deadline.data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.application_deadline.data = None

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    category = StringField('Category', validators=[Length(max=50)])
    submit = SubmitField('Create')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=8)])
    is_admin = BooleanField('Is Admin')
    submit = SubmitField('Create')

class BotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=255)])
    submit = SubmitField('Submit')

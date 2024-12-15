from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, Email
from app.models.organization import Organization
from app.forms.fields import CustomDateTimeField
from app.models.tag import Tag
from app.models.user import User
from app.models.bot import Bot

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    summary = TextAreaField('Summary', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    homepage_url = URLField('Homepage URL', validators=[Optional()])
    application_procedure = TextAreaField('Application Procedure', validators=[Optional()])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[Optional()])
    application_deadline = CustomDateTimeField(
        'Application Deadline',
        format='%Y-%m-%d %H:%M:%S',
        validators=[Optional()]
    )
    open_for_applications = BooleanField('Open for Applications', default=False)
    submit = SubmitField('Create')

    def validate_application_deadline(self, field):
        # If user provided a value but it wasn't parsed into a datetime, raise the custom error.
        if field.raw_data and field.raw_data[0] and field.data is None:
            raise ValidationError("Invalid date format. Please use YYYY-MM-DD HH:MM:SS.")

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    category = StringField('Category', validators=[DataRequired(), Length(max=100)])  # Added this line
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if not name.data:
            raise ValidationError('Name cannot be empty.')
        if self.original_name and name.data == self.original_name:
            return  # Skip validation if the name hasn't changed
        tag = Tag.query.filter_by(name=name.data).first()
        if tag:
            raise ValidationError('Tag with this name already exists.')

    def validate_category(self, category):
        if not category.data:
            raise ValidationError('Category cannot be empty.')

class TagForm(FlaskForm):
    name = StringField('Tag Name', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Submit')

class BotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    status = StringField('Status', validators=[Length(max=255)])
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(BotForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            bot = Bot.query.filter_by(name=name.data).first()
            if bot:
                raise ValidationError('Bot with this name already exists.')

class OrganizationForm(FlaskForm):
    name = StringField('Org Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('About')
    homepage_url = URLField('Website', validators=[Optional()])
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.original_name = original_name or None

    def validate_name(self, name):
        if name.data != self.original_name:
            organization = Organization.query.filter_by(name=name.data).first()
            if organization:
                raise ValidationError('Organization with this name already exists.')

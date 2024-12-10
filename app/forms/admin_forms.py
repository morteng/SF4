from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.stipend import Stipend
from .fields import NullableDateTimeField  # Import the custom field

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    summary = TextAreaField('Summary')
    description = TextAreaField('Description')
    homepage_url = URLField('Homepage URL', validators=[Length(max=255)])
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = NullableDateTimeField('Application Deadline (YYYY-MM-DD HH:MM:SS)')
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(StipendForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if self.original_name is not None and name.data != self.original_name:
            stipend = Stipend.query.filter_by(name=name.data).first()
            if stipend:
                raise ValidationError('Stipend with this name already exists.')

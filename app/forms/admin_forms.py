from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.stipend import Stipend
from datetime import datetime

class NullableDateTimeField(StringField):
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0].strip():
            try:
                self.data = datetime.strptime(valuelist[0], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.data = None
        else:
            self.data = None

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    summary = TextAreaField('Summary')  # Ensure this field is present and not restricted
    description = TextAreaField('Description')
    homepage_url = URLField('Homepage URL', validators=[Length(max=255)])
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = NullableDateTimeField('Application Deadline (YYYY-MM-DD HH:MM:SS)')  # Use the custom field
    open_for_applications = BooleanField('Open for Applications')
    submit = SubmitField('Create')

    def __init__(self, original_name=None, *args, **kwargs):
        super(StipendForm, self).__init__(*args, **kwargs)
        if original_name:
            self.name.data = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            stipend = Stipend.query.filter_by(name=name.data).first()
            if stipend:
                raise ValidationError('Stipend with this name already exists.')

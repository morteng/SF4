from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.stipend import Stipend

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    summary = TextAreaField('Summary', validators=[Length(max=255)])
    description = TextAreaField('Description')
    homepage_url = StringField('Homepage URL', validators=[Length(max=255)])
    application_procedure = TextAreaField('Application Procedure')
    eligibility_criteria = TextAreaField('Eligibility Criteria')
    application_deadline = StringField('Application Deadline (YYYY-MM-DD HH:MM:SS)')
    open_for_applications = BooleanField('Open for Applications')

    def __init__(self, original_name=None, *args, **kwargs):
        super(StipendForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            stipend = Stipend.query.filter_by(name=name.data).first()
            if stipend:
                raise ValidationError('Stipend with this name already exists.')

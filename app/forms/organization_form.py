from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class OrganizationForm(FlaskForm):
    name = StringField('Organization Name', validators=[DataRequired()])
    description = StringField('Description')
    homepage_url = StringField('Homepage URL', validators=[DataRequired()])
    submit = SubmitField('Submit')

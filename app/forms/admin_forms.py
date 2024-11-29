from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class StipendForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    # Add other fields with validators as needed
    submit = SubmitField('Create')

class TagForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    category = StringField('Category', validators=[Length(max=50)])
    submit = SubmitField('Create')

class OrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Description', validators=[Length(max=255)])
    homepage_url = StringField('Homepage URL', validators=[Length(max=255)])
    submit = SubmitField('Create')

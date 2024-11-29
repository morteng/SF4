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

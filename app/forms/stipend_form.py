from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class StipendForm(FlaskForm):
    name = StringField('Stipend Name', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    organization_id = StringField('Organization ID')
    submit = SubmitField('Submit')

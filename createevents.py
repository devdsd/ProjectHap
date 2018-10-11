from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class CreateEvent(FlaskForm):
    eventName = StringField('Event Name', 
        validators=[DataRequired(), Length(min=2, max =50)])
    location = StringField('Location', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    registrationFee = StringField('Fee', validators=[DataRequired()])
    submit = SubmitField('Submit')

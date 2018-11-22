from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField
# from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from hap.models import Users, Categories
# from hap.models import categories_query

class SignupForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    interestoption = SelectField('Choose an Interest', choices=[(interest.id, interest.categoryName) for interest in Categories.query.all()], validators=[DataRequired()])

    submit = SubmitField('SIGN UP')

    def validate_username(self, username):
		user = Users.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("Username already taken.")

    def validate_email(self, email):
		user = Users.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("Email already used.")

class LoginForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
  password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=50)])
  remember = BooleanField('Remember Password')
  
  submit = SubmitField('Log in')


class UpdateEventForm(FlaskForm):
    eventName = StringField('Event Name', validators=[DataRequired(), Length(min=2, max =50)])
    eventDescription = TextAreaField('Event Description', validators=[DataRequired()])
    eventDate = DateField('Event Date', format='%Y-%m-%d')
    startTime = TimeField("Event Start Time", validators=[DataRequired()])
    endTime = TimeField("Event End Time", validators=[DataRequired()])
    imageFile = FileField("Profile Picture", validators=[FileAllowed(["jpg", "png"])])
    fee = IntegerField("Fee", validators=[NumberRange(max=1000000)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max =75)])
    submit = SubmitField('Update')


class CreateEventForm(FlaskForm):
    eventName = StringField('Event Name', validators=[DataRequired(), Length(min=2, max =50)])
    eventDescription = TextAreaField('Event Description', validators=[DataRequired()])
    eventDate = DateField('Event Date', format='%Y-%m-%d')
    startTime = TimeField("Event Start Time", validators=[DataRequired()])
    endTime = TimeField("Event End Time", validators=[DataRequired()])
    imageFile = FileField("Profile Picture", validators=[FileAllowed(["jpg", "png"])])
    fee = IntegerField("Fee", validators=[NumberRange(max=1000000)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max =75)])
    submit = SubmitField('Post')

class UpdateAccountForm(FlaskForm):
      firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
      lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
      username = StringField('Username', validators=[DataRequired(),Length(min=2, max=20)])
      email = StringField('Email', validators=[DataRequired(), Email()])
      picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
      submit = SubmitField('Update')
      
      def validate_username(self, username):
        if username.data != current_user.username:
          user = Users.query.filter_by(username=username.data).first()
          if user:
            raise ValidationError("Username already taken.")
      
      def validate_email(self, email):
        if email.data != current_user.email:
          user = Users.query.filter_by(email=email.data).first()
          if user:
              raise ValidationError("Email already used.")

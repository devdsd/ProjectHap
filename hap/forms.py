from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from hap.models import Users, Categories

class BasicAccountInfoForm(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
  lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
  email = StringField('Email', validators=[DataRequired(), Email()])
  username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
  password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=50)])
  confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

  submit = SubmitField('Sign Up')

  def validate_username(self, username):
    user = Users.query.filter_by(username=username.data).first()
    if user:
      raise ValidationError("Username already taken.")

  def validate_email(self, email):
    user = Users.query.filter_by(email=email.data).first()
    if user:
      raise ValidationError("Email already used.")

class UserInterestForm(FlaskForm):
  submit = SubmitField('Next', id="followInterests")

class SetUpAccount(FlaskForm):
  profPic = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

  submit = SubmitField('Hop In')

class LoginForm(FlaskForm):
  usernameOrEmail = StringField('Username or Email Address', validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=50)])
  remember = BooleanField('Remember Password')
  
  submit = SubmitField('Log In')

  def validate_usernameOrEmail(self, usernameOrEmail):
    bool = False
    for x in usernameOrEmail.data:
      if x == "@":
        bool = True

    if bool == True:
      user = Users.query.filter_by(email=usernameOrEmail.data).first()
      if user is None:
        raise ValidationError("Enter valid username or email address.")
    else:
      user = Users.query.filter_by(username=usernameOrEmail.data).first()
      if user is None:
        raise ValidationError("Enter valid username or email address.")

class UpdateAccountForm(FlaskForm):
  firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
  lastName = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
  username = StringField('Username', validators=[DataRequired(),Length(min=2, max=20)])
  email = StringField('Email', validators=[DataRequired(), Email()])
  picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
  submit = SubmitField('Update Account')

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

class UpdateEventForm(FlaskForm):
  eventName = StringField('Event Name', validators=[DataRequired(), Length(min=2, max =80)])
  eventDescription = TextAreaField('Event Description', validators=[DataRequired()])
  eventDate = DateField('Event Date', format='%Y-%m-%d')
  startTime = TimeField("Event Start Time", validators=[DataRequired()])
  endTime = TimeField("Event End Time", validators=[DataRequired()])
  imageFile = FileField("Profile Picture", validators=[FileAllowed(["jpg", "png"])])
  fee = IntegerField("Fee", validators=[NumberRange(max=1000000)])
  location = StringField('Location', validators=[DataRequired(), Length(min=2, max =75)])
  submit = SubmitField('Update Event')

class CreateEventForm(FlaskForm):
  eventName = StringField('Event Name', validators=[DataRequired(), Length(min=2, max=80)])
  eventDescription = TextAreaField('Event Description', validators=[DataRequired()])
  eventDate = DateField('Event Date', format='%Y-%m-%d')
  startTime = TimeField("Event Start Time", validators=[DataRequired()])
  endTime = TimeField("Event End Time", validators=[DataRequired()])
  imageFile = FileField("Event Banner", validators=[FileAllowed(["jpg", "png"])])
  fee = IntegerField("Fee", validators=[NumberRange(max=1000000)])
  location = StringField('Location', validators=[DataRequired(), Length(min=2, max =75)])
  categoryoption = SelectField('Choose a Category of Event', coerce=int, choices=[(category.id, category.categoryName) for category in Categories.query.all()])
  submit = SubmitField('Post Event')

class DeleteEventForm(FlaskForm):
  eventName = StringField('Event Name', validators=[Length(min=2, max =80)])
  confirm_eventName = StringField('Confirm Event Name', validators=[DataRequired(), Length(min=2, max =80), EqualTo('eventName')])
  submit = SubmitField("Delete Event")

class JoinEventForm(FlaskForm):
  submit = SubmitField("Join Event")

class UnjoinEventForm(FlaskForm):
  submit = SubmitField("Unjoin Event")
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


app = Flask(__name__)

app.config['SECRET_KEY'] = '2BB80D537B1DA3E38BD30361AA855686BDE0EACD7162FEF6A25FE97BF527A25B'


class SignupForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    # def validate_username(self, username):
	# 	user = User.query.filter_by(username=username.data).first()
	# 	if user:
	# 		raise ValidationError('That username is already taken. Please choose different one!')

    # def validate_email(self, email):
	# 	user = User.query.filter_by(email=email.data).first()
	# 	if user:
	# 		raise ValidationError('That email is already taken. Please choose different one!')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')

	submit = SubmitField('Login')

class CreateEvent(FlaskForm):
    eventName = StringField('Event Name', 
        validators=[DataRequired(), Length(min=2, max =50)])
    location = StringField('Location', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    registrationFee = StringField('Fee', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home Page')


@app.route('/about')
def about():
    return render_template('about.html', title='About Hap')


@app.route('/createevent', methods=['GET', 'POST'])
def createevent():
    form = CreateEvent()
    if form.validate_on_submit():
        flash('Event Created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('createevent.html', title='Create Event', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        flash('Account create successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    return render_template('login.html', title='Log In', form=form)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
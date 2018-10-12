from flask import render_template, url_for, flash, redirect, request
from hap import app
from hap.forms import SignupForm, LoginForm, CreateEventForm

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
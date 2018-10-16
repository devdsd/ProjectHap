from flask import render_template, url_for, flash, redirect, request
from hap import app, bcrypt
from hap.forms import SignupForm, LoginForm, CreateEventForm
from hap import models
from hap.models import *
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home Page')


@app.route('/about')
def about():
    return render_template('about.html', title='About Hap')


@app.route('/createevent', methods=['GET', 'POST'])
def createevent():
    form = CreateEventForm()
    if form.validate_on_submit():
        flash('Event Created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('createevent.html', title='Create Event', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # User registration 
        user = Users(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Account successfully created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user_username = Users.query.filter_by(username=form.username.data).first()
        user_email = Users.query.filter_by(email=form.email.data).first()
        if (user_username or user_email) and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful! Please check username/email and password', 'danger')
            
    return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title = 'Account')
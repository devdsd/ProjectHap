import os, binascii
from PIL import Image
from hap import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request
from hap.forms import SignupForm, LoginForm, CreateEventForm, UpdateAccountForm
# from hap import models
from hap.models import *
from flask_login import login_user, current_user, logout_user, login_required

def save_picture(form_picture):
    random_hex = binascii.b2a_hex(os.urandom(15))
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/images', picture_fn)
    
    output_size=(400,400)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route('/', methods=["GET","POST"])
@app.route('/home', methods=["GET","POST"])
def home():
    if current_user.is_authenticated:
        formTwo = CreateEventForm()
        events = Events.query.all()
        if formTwo.validate_on_submit():
            picture_file = ""
            if formTwo.imageFile.data:
                picture_file = save_picture(formTwo.imageFile.data)

            event = Events(image_file=picture_file, eventName=formTwo.eventName.data, eventDate=formTwo.eventDate.data, eventStartTime=formTwo.startTime.data, eventEndTime=formTwo.endTime.data, eventDescription=formTwo.eventDescription.data, fee=formTwo.fee.data, location=formTwo.location.data, host=current_user)
            
            db.session.add(event)
            db.session.commit()

            flash("Your event has been created.", "success")
            return redirect(url_for("home"))
        
        elif formTwo.eventName.data:
            flash("Create unsuccessful. Please try again.", "danger")

        return render_template("home.html", title="Home", formTwo=formTwo, homeNavbarLogoBorderBottom="#FFC000", profileNavbarLogoBorderBottom="white", events=events)

    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Log in unsuccessful.", "danger")
    elif form.email.data or form.password.data:
        return render_template("home.html", form=form, title="Welcome to Hap!", dropdownAppearance="show", ariaExpansionBool="true")
        
    return render_template("home.html", form=form, title="Welcome to Hap!", dropdownAppearance="", ariaExpansionBool="false")


@app.route('/about')
def about():
    return render_template('about.html', title='About Hap')


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

        flash("Account created successfully.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        # user_email = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("home"))
            # return redirect(url_for('home'))
        else:
            flash("Log in unsuccessful.", "danger")

    return render_template('login.html', title='Log In', form=form)

@app.route('/landing')
def landing():
    return render_template('landingpage.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    
    profilePic = url_for("static", filename="images/" + current_user.image_file)
    return render_template("account.html", title="Account", homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        current_user.username = form.username.data
        current_user.email = form.email.data
            
        db.session.commit()

        flash("You profile has been updated.", "success")
        
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.firstName.data = current_user.firstName;
        form.lastName.data = current_user.lastName;
        form.username.data = current_user.username;
        form.email.data = current_user.email;

    return render_template("settings.html", title="Settings", form=form, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")

@app.route("/event/<int:event_id>")
@login_required
def event(event_id):
    event = Events.query.get_or_404(event_id)
    
    return render_template("event.html", title=event.eventName, event=event, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")


# Noted Problems: 
#     > After creating account >> it must go to login page first to login not automatically login after creating the account
#     > Account.html >> form is not defined
#     > 


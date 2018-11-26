import os, binascii
from PIL import Image
from hap import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
from hap.forms import *
from hap.models import *
from flask_login import login_user, current_user, logout_user, login_required


def save_picture(form_picture, size):
    random_hex = binascii.b2a_hex(os.urandom(15))
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/images', picture_fn)
    
    output_size=(size, size)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route('/', methods=["GET","POST"])
@app.route('/home', methods=["GET","POST"])
def home():
    if current_user.is_authenticated:
        formTwo = CreateEventForm()
        # events = Events.query.order_by(Events.dateCreated.desc())
        userinterest = userhasinterest_rel_table.query.filter().first()
        events = Events.query.filter(Categories.eventhascategory.any(id=category.id)).order_by(Events.dateCreated.desc()).all()
        # print "Ambot nimo !"

        if formTwo.validate_on_submit():
            picture_file = ""
            picture_file_sm = ""
            if formTwo.imageFile.data is not None:
                picture_file = save_picture(formTwo.imageFile.data, 1000)
                picture_file_sm = save_picture(formTwo.imageFile.data, 500)

                event = Events(image_file=picture_file, image_file_sm=picture_file_sm, eventName=formTwo.eventName.data, eventDate=formTwo.eventDate.data, eventStartTime=formTwo.startTime.data, eventEndTime=formTwo.endTime.data, eventDescription=formTwo.eventDescription.data, fee=formTwo.fee.data, location=formTwo.location.data, host=current_user)
                
                db.session.add(event)
                db.session.commit()

                # foreventId = Events.query.filter_by(id=event.id).first()
        
                statement = eventhascategory_rel_table.insert().values(category_id=formTwo.categoryoption.data, event_id=event.id)
                db.session.execute(statement)
                db.session.commit()

            else:
                event = Events(eventName=formTwo.eventName.data, eventDate=formTwo.eventDate.data, eventStartTime=formTwo.startTime.data, eventEndTime=formTwo.endTime.data, eventDescription=formTwo.eventDescription.data, fee=formTwo.fee.data, location=formTwo.location.data, host=current_user)
            
                db.session.add(event)
                db.session.commit()

                statement = eventhascategory_rel_table.insert().values(category_id=formTwo.categoryoption.data, event_id=event.id)
                db.session.execute(statement)
                db.session.commit()

                
            flash("Your event has been created.", "success")
            return redirect(url_for("home"))


        elif formTwo.eventName.data:
            flash("Create event unsuccessful.", "danger")
            return redirect(url_for("home"))

        # print formTwo.categoryoption.data

        return render_template("home.html", title="Home", formTwo=formTwo, homeNavbarLogoBorderBottom="#FFC000", profileNavbarLogoBorderBottom="white", events=events)

    formOne = LoginForm()

    if formOne.validate_on_submit():
        user = Users.query.filter_by(email=formOne.usernameOrEmail.data).first()
        if user is not None:
            if bcrypt.check_password_hash(user.password, formOne.password.data) == True:
                login_user(user, remember=formOne.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Log in unsuccessful.", "danger")
                return render_template("home.html", formOne=formOne, title="Welcome to Hap!", dropdownAppearance="show", ariaExpansionBool="true")
        else:
            user = Users.query.filter_by(username=formOne.usernameOrEmail.data).first()
            
            if user and bcrypt.check_password_hash(user.password, formOne.password.data):
                login_user(user, remember=formOne.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Log in unsuccessful.", "danger")
                return render_template("home.html", formOne=formOne, title="Welcome to Hap!", dropdownAppearance="show", ariaExpansionBool="true")

    elif formOne.usernameOrEmail.data or formOne.password.data:
        return render_template("home.html", formOne=formOne, title="Welcome to Hap!", dropdownAppearance="show", ariaExpansionBool="true")
        
    return render_template("home.html", formOne=formOne, title="Welcome to Hap!", dropdownAppearance="", ariaExpansionBool="false")


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
        
        user = Users(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        forUserId = Users.query.filter_by(username=form.username.data).first()
        
        statement = userhasinterest_rel_table.insert().values(category_id=form.interestoption.data, user_id=forUserId.id)
        db.session.execute(statement)
        db.session.commit()

        login_user(user)
        return redirect(url_for('home'))

    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.usernameOrEmail.data).first()
        if user is not None:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Log in unsuccessful.", "danger")
        else:
            user = Users.query.filter_by(username=form.usernameOrEmail.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Log in unsuccessful.", "danger")

    return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/<username>', methods=['GET', 'POST'])
@login_required
def account(username):
    if username == current_user.username:
        user = current_user
        profilePic = url_for("static", filename="images/" + current_user.image_file)
        events = Events.query.filter_by(user_id=current_user.id).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=current_user.id).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(id=current_user.id)).count()
        interest = Categories.query.filter(Categories.userhasinterest.any(id=current_user.id)).first()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="underline", interest=interest)
    else:
        user = Users.query.filter_by(username=username).first()
        profilePic = url_for("static", filename="images/" + user.image_file)
        events = Events.query.filter_by(user_id=user.id).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=user.id).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(id=user.id)).count()
        interest = Categories.query.filter(Categories.userhasinterest.any(id=current_user.id)).first()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="underline", interest=interest)

@app.route("/<username>/accountevents")
@login_required
def account_events(username):
    if username == current_user.username:
        user = current_user
        profilePic = url_for("static", filename="images/" + current_user.image_file)
        events = Events.query.filter_by(user_id=current_user.id).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=current_user.id).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(id=current_user.id)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="underline")
    else:
        user = Users.query.filter_by(username=username).first()
        profilePic = url_for("static", filename="images/" + user.image_file)
        events = Events.query.filter_by(user_id=user.id).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=user.id).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(id=user.id)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="underline")

@app.route("/<username>/joinedevents")
@login_required
def joined_events(username):
    if username == current_user.username:
        user = current_user
        profilePic = url_for("static", filename="images/" + current_user.image_file)
        events = Events.query.filter(Events.joinrel.any(id=current_user.id)).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=current_user.id).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(id=current_user.id)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarJoinedEventsUnderline="underline")
    else:
        user = Users.query.filter_by(username=username).first()
        profilePic = url_for("static", filename="images/" + user.image_file)
        events = Events.query.filter(Events.joinrel.any(id=user.id)).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=user.id).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(id=user.id)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarJoinedEventsUnderline="underline")

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 1000)
            picture_file_sm = save_picture(form.picture.data, 500)
            current_user.image_file = picture_file
            current_user.image_file_sm = picture_file_sm
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        current_user.username = form.username.data
        current_user.email = form.email.data
            
        db.session.commit()

        flash("Your profile has been updated.", "success")
        
        return redirect(url_for("account", username=current_user.username))

    elif request.method == "GET":
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("settings.html", title="Settings", form=form, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")

@app.route("/event/<int:event_id>", methods=["GET", "POST"])
@login_required
def event(event_id):
    event = Events.query.get_or_404(event_id)

    formFour = DeleteEventForm()
    formThree = UpdateEventForm()

    formFour.eventName.data = event.eventName

    if formFour.validate_on_submit():
        db.session.delete(event)
        db.session.commit()
        flash("Your event has been deleted.", "success")

        return redirect(url_for('home'))
        
    elif formFour.confirm_eventName.data:
        flash("Delete event unsuccessful.", "danger")
        return redirect(url_for('event', event_id=event.id))
    
    if formThree.validate_on_submit():
        if formThree.imageFile.data:
            imageFile = save_picture(formThree.imageFile.data, 1000)
            imageFilesm = save_picture(formThree.imageFile.data, 500)
            event.image_file = imageFile
            event.image_file_sm = imageFilesm
        event.eventName = formThree.eventName.data
        event.eventDescription = formThree.eventDescription.data
        event.eventDate = formThree.eventDate.data
        event.eventStartTime = formThree.startTime.data
        event.eventEndTime = formThree.endTime.data
        event.fee = formThree.fee.data
        event.location = formThree.location.data  
        db.session.commit()
        flash("Your Event has been updated.", "success")
        return redirect(url_for('event', event_id=event.id))

    if request.method == "GET":
        formThree.eventName.data = event.eventName
        formThree.eventDescription.data = event.eventDescription
        formThree.eventDate.data = event.eventDate
        formThree.startTime.data = event.eventStartTime
        formThree.endTime.data = event.eventEndTime
        formThree.fee.data = event.fee
        formThree.location.data = event.location

    if event.host != current_user:
        joinedEvents = Events.query.filter(Events.joinrel.any(id=current_user.id)).all()

        bool = False
        for joinedEvent in joinedEvents:
            if joinedEvent.id == event.id:
                bool = True
        
        if bool == True:
            formTwo = UnjoinEventForm()
            
            if formTwo.validate_on_submit():
                bool = False

                statement = join_rel_table.delete().where(join_rel_table.c.user_id==current_user.id).where(join_rel_table.c.event_id==event.id)
                
                db.session.execute(statement)
                db.session.commit()

                return redirect(url_for("event", event_id=event.id))
            
            return render_template("event.html", title=event.eventName, event=event, formOneOrTwo=formTwo, formButtonClass="danger", homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")

        else:
            formOne = JoinEventForm()

            if formOne.validate_on_submit():
                statement = join_rel_table.insert().values(event_id=event.id, user_id=current_user.id)

                db.session.execute(statement)
                db.session.commit()

                return redirect(url_for("event", event_id=event.id))

            return render_template("event.html", title=event.eventName, event=event, formOneOrTwo=formOne, formButtonClass="warning", homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")

    return render_template("event.html", title=event.eventName, event=event, formThree=formThree, formFour=formFour, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")
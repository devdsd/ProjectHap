import os, binascii
from PIL import Image
from hap import app, db, bcrypt, mail
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, session
from hap.forms import *
from hap.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask import request
from flask_mail import Message


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
        
        if current_user.numberOfLogins == 0:
            return redirect(url_for("setup_acc"))

        userFeedEvents = db.session.query(eventhascategory_rel_table, userhasinterest_rel_table, Events.eventName, Events.location, Events.eventId, Events.user_id, Events.image_file, Events.eventDate, Events.eventStartTime, Events.eventEndTime, Events.host, Users.userId).filter(Users.userId==current_user.userId).filter(Events.eventId==eventhascategory_rel_table.c.event_id).filter(eventhascategory_rel_table.c.category_id==userhasinterest_rel_table.c.category_id).filter(userhasinterest_rel_table.c.user_id==current_user.userId).order_by(Events.dateCreated.desc()).all()
        events = Events.query.all()

        display = []
        for c, event in enumerate(userFeedEvents):
            dict = {}
            dict["event_id"] = event.eventId
            dict["category_id"] = event.category_id
            dict["user_id"] = event.userId
            dict["event_name"] = event.eventName
            dict["event_location"] = event.location
            dict["event_imgFile"] = event.image_file
            dict["event_date_dayNum"] = event.eventDate.strftime("%d")
            dict["event_date_dayName"] = event.eventDate.strftime("%a")
            dict["event_date_month"] = event.eventDate.strftime("%b")
            dict["event_startTime"] = event.eventStartTime.strftime("%I %p")
            dict["event_endTime"] = event.eventEndTime

            display.append(dict)

        for x, event in enumerate(display):
            selectEvent = Events.query.filter_by(eventId=event["event_id"]).first()
            event["host_id"] = selectEvent.host.userId
            event["host_username"] = selectEvent.host.username
            event["host_firstName"] = selectEvent.host.firstName
            event["host_lastName"] = selectEvent.host.lastName

        if formTwo.validate_on_submit():
            picture_file = ""
            picture_file_sm = ""
            if formTwo.imageFile.data is not None:
                picture_file = save_picture(formTwo.imageFile.data, 1000)
                picture_file_sm = save_picture(formTwo.imageFile.data, 500)

                event = Events(image_file=picture_file, image_file_sm=picture_file_sm, eventName=formTwo.eventName.data, eventDate=formTwo.eventDate.data, eventStartTime=formTwo.startTime.data, eventEndTime=formTwo.endTime.data, eventDescription=formTwo.eventDescription.data, fee=formTwo.fee.data, location=formTwo.location.data, host=current_user)
                
                db.session.add(event)
                db.session.commit()

                statement = eventhascategory_rel_table.insert().values(category_id=formTwo.categoryoption.data, event_id=event.eventId)
                db.session.execute(statement)
                db.session.commit()

            else:
                event = Events(eventName=formTwo.eventName.data, eventDate=formTwo.eventDate.data, eventStartTime=formTwo.startTime.data, eventEndTime=formTwo.endTime.data, eventDescription=formTwo.eventDescription.data, fee=formTwo.fee.data, location=formTwo.location.data, host=current_user)
            
                db.session.add(event)
                db.session.commit()

                statement = eventhascategory_rel_table.insert().values(category_id=formTwo.categoryoption.data, event_id=event.eventId)
                db.session.execute(statement)
                db.session.commit()

                
            flash("Your event has been created.", "success")
            return redirect(url_for("home"))


        elif formTwo.eventName.data:
            flash("Create event unsuccessful.", "danger")
            return redirect(url_for("home"))

        return render_template("home.html", title="Home", formTwo=formTwo, homeNavbarLogoBorderBottom="#FFC000", profileNavbarLogoBorderBottom="white", display=display)

    formOne = LoginForm()

    if formOne.validate_on_submit():
        user = Users.query.filter_by(email=formOne.usernameOrEmail.data).first()
        if user is not None:
            if bcrypt.check_password_hash(user.password, formOne.password.data) == True:
                login_user(user, remember=formOne.remember.data)

                user.numberOfLogins = user.numberOfLogins + 1
                db.session.commit()

                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Log in unsuccessful.", "danger")
                return render_template("home.html", formOne=formOne, title="Welcome to Hap!", dropdownAppearance="show", ariaExpansionBool="true")
        else:
            user = Users.query.filter_by(username=formOne.usernameOrEmail.data).first()
            
            if user and bcrypt.check_password_hash(user.password, formOne.password.data):
                login_user(user, remember=formOne.remember.data)

                user.numberOfLogins = user.numberOfLogins + 1
                db.session.commit()

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

    formOne = BasicAccountInfoForm()

    if formOne.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(formOne.password.data).decode('utf-8')

        user = Users(firstName=formOne.firstName.data, lastName=formOne.lastName.data, username=formOne.username.data, email=formOne.email.data, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('interests'))

    return render_template('signup.html', title='Sign Up', formOne=formOne)

@app.route('/interests', methods=['GET', 'POST'])
@login_required
def interests():
    if current_user.numberOfLogins != 0:
        return redirect(url_for("acc_info_settings"))

    userInterests = db.session.query(Categories.catId, Categories.categoryName, userhasinterest_rel_table.c.user_id).filter(Categories.catId==userhasinterest_rel_table.c.category_id).filter(userhasinterest_rel_table.c.user_id==current_user.userId).order_by(Categories.catId.asc()).all()
    categories = Categories.query.all()

    display = []
    for c, category in enumerate(categories):
        dict = {}
        dict["id"] = category.catId
        dict["categoryName"] = category.categoryName

        display.append(dict)

    for x, interest in enumerate(userInterests):
        for y, category in enumerate(categories):
            if category.catId == interest.catId:
                dict = {}
                dict["id"] = interest.catId
                dict["categoryName"] = interest.categoryName
                dict["user_id"] = interest.user_id
                display[y] = dict

    formOne = UserInterestForm()

    if formOne.validate_on_submit():
        return redirect(url_for('setup_acc'))

    return render_template('gettingstartedinterests.html', title='Getting Started', formOne=formOne, display=display, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")

@app.route('/follow', methods=['POST'])
@login_required
def follow():
    req = request.form['category_id']

    lookRow = db.session.query(userhasinterest_rel_table).filter(userhasinterest_rel_table.c.user_id==current_user.userId, userhasinterest_rel_table.c.category_id==req).first()

    if lookRow is None:
        statement =  userhasinterest_rel_table.insert().values(user_id=current_user.userId, category_id=req)

        db.session.execute(statement)
        db.session.commit()

    return jsonify({'result' : 'success'})

@app.route('/unfollow', methods=['POST'])
@login_required
def unfollow():
    statement = userhasinterest_rel_table.delete().where(userhasinterest_rel_table.c.user_id==current_user.userId).where(userhasinterest_rel_table.c.category_id==request.form['category_id'])
                
    db.session.execute(statement)
    db.session.commit()

    return jsonify({'result' : 'success'})

@app.route('/setupacc', methods=['GET', 'POST'])
@login_required
def setup_acc():
    if current_user.numberOfLogins != 0:
        return redirect(url_for("acc_info_settings"))

    formOne = SetUpAccount()

    if formOne.validate_on_submit():
        picture_file = ""
        picture_file_sm = ""

        if formOne.profPic.data is not None:
            picture_file = save_picture(formOne.profPic.data, 1000)
            picture_file_sm = save_picture(formOne.profPic.data, 500)

            setattr(current_user, 'image_file', picture_file)
            setattr(current_user, 'image_file_sm', picture_file_sm)

        current_user.numberOfLogins = current_user.numberOfLogins + 1

        db.session.commit()

        return redirect(url_for('home'))

    profilePic = url_for("static", filename="images/" + current_user.image_file)
    return render_template('gettingstartedsetupacc.html', title='Getting Started', formOne=formOne, profilePic=profilePic, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")

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

                user.numberOfLogins = user.numberOfLogins + 1
                db.session.commit()

                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Log in unsuccessful.", "danger")
        else:
            user = Users.query.filter_by(username=form.usernameOrEmail.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)

                user.numberOfLogins = user.numberOfLogins + 1
                db.session.commit()

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
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    if username == current_user.username:
        user = current_user
        userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
        profilePic = url_for("static", filename="images/" + current_user.image_file_sm)
        events = Events.query.filter_by(user_id=current_user.userId).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=current_user.userId).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=current_user.userId)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="underline", userInterests=userInterests)
    else:
        selectUser = Users.query.filter_by(username=username).first()
        if selectUser:
            user = Users.query.get_or_404(selectUser.userId)
            userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
            profilePic = url_for("static", filename="images/" + user.image_file_sm)
            events = Events.query.filter_by(user_id=user.userId).order_by(Events.dateCreated.desc())
            createdEventsCount = Events.query.filter_by(user_id=user.userId).count()
            joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=user.userId)).count()
            return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="underline", userInterests=userInterests)
        
        elif selectUser is None:
            return redirect(url_for("home"))

@app.route("/<username>/accountevents")
@login_required
def account_events(username):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    if username == current_user.username:
        user = current_user
        userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
        profilePic = url_for("static", filename="images/" + current_user.image_file_sm)
        events = Events.query.filter_by(user_id=current_user.userId).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=current_user.userId).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=current_user.userId)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="underline", userInterests=userInterests)
    else:
        user = Users.query.get_or_404(username)
        userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
        profilePic = url_for("static", filename="images/" + user.image_file_sm)
        events = Events.query.filter_by(user_id=user.userId).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=user.userId).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=user.userId)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="underline", userInterests=userInterests)

@app.route("/<username>/joinedevents")
@login_required
def joined_events(username):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    if username == current_user.username:
        user = current_user
        userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
        profilePic = url_for("static", filename="images/" + current_user.image_file_sm)
        events = Events.query.filter(Events.joinrel.any(userId=current_user.userId)).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=current_user.userId).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=current_user.userId)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarJoinedEventsUnderline="underline", userInterests=userInterests)
    else:
        user = Users.query.get_or_404(username)
        userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
        profilePic = url_for("static", filename="images/" + user.image_file_sm)
        events = Events.query.filter(Events.joinrel.any(userId=user.userId)).order_by(Events.dateCreated.desc())
        createdEventsCount = Events.query.filter_by(user_id=user.userId).count()
        joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=user.userId)).count()
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarJoinedEventsUnderline="underline", userInterests=userInterests)

@app.route("/settings/accountinfo", methods=["GET", "POST"])
@login_required
def acc_info_settings():
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    formOne = UpdateAccountForm()

    if formOne.validate_on_submit():
        if formOne.picture.data:
            picture_file = save_picture(formOne.picture.data, 1000)
            picture_file_sm = save_picture(formOne.picture.data, 500)
            current_user.image_file = picture_file
            current_user.image_file_sm = picture_file_sm
        current_user.firstName = formOne.firstName.data
        current_user.lastName = formOne.lastName.data
        current_user.username = formOne.username.data
        current_user.email = formOne.email.data
            
        db.session.commit()

        flash("Your profile has been updated.", "success")
        
        return redirect(url_for("account", username=current_user.username))

    elif request.method == "GET":
        formOne.firstName.data = current_user.firstName
        formOne.lastName.data = current_user.lastName
        formOne.username.data = current_user.username
        formOne.email.data = current_user.email

    leftPanelItems = [['user.svg','acc_info_settings','Account Information'],['key.svg','security_settings','Security'],['controls.svg','interest_pref_settings','Interest Preferences']]
    profilePic = url_for("static", filename="images/" + current_user.image_file)
    return render_template("accinfosettings.html", title="Settings", formOne=formOne, leftPanelItems=leftPanelItems, profilePic=profilePic, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", itemUnderline="underline;")

@app.route("/settings/security", methods=["GET", "POST"])
@login_required
def security_settings():
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    leftPanelItems = [['user.svg','acc_info_settings','Account Information'],['key.svg','security_settings','Security'],['controls.svg','interest_pref_settings','Interest Preferences']]

    return render_template("securitysettings.html", title="Settings", leftPanelItems=leftPanelItems, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", itemUnderline="underline;")

@app.route("/settings/interestpreferences", methods=["GET", "POST"])
@login_required
def interest_pref_settings():
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    leftPanelItems = [['user.svg','acc_info_settings','Account Information'],['key.svg','security_settings','Security'],['controls.svg','interest_pref_settings','Interest Preferences']]

    return render_template("interestprefsettings.html", title="Settings", leftPanelItems=leftPanelItems, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", itemUnderline="underline;")

@app.route("/event/<int:event_id>", methods=["GET", "POST"])
@login_required
def event(event_id):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    event = Events.query.get_or_404(event_id)
    category = Categories.query.filter(Categories.eventhascategory.any(eventId=event_id)).first()

    reviewbody = ReviewForm()
    # print "1. Print this: {}".format(reviewbody.reviewbody.data)

    if reviewbody.reviewbody.data is not None:
        # print "NAA ko sa REVIEW BODY"
        statement = review_rel_table.insert().values(user_id=current_user.userId, event_id=event.eventId, review=reviewbody.reviewbody.data)
        db.session.execute(statement)
        db.session.commit()

        # print "2. Print this: {}".format(event.id)

        return redirect(url_for("event", event_id=event.eventId))

    reviews = db.session.query(review_rel_table.c.review, Users.firstName, Users.lastName).filter(review_rel_table.c.event_id == event.eventId).filter(Users.userId == review_rel_table.c.user_id).order_by(review_rel_table.c.dateCreated.desc()).all()
    # reviews = Events.query.join(review_rel_table).join(Users).filter(review_rel_table.c.user_id == current_user.id and review_rel_table.c.event_id == event.id).all()
    # print "3. Print this: {}".format(reviews)

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
        return redirect(url_for('event', event_id=event.eventId))
    
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
        joinedEvents = Events.query.filter(Events.joinrel.any(userId=current_user.userId)).all()

        bool = False
        for joinedEvent in joinedEvents:
            if joinedEvent.eventId == event.eventId:
                bool = True
        
        if bool == True:
            formTwo = UnjoinEventForm()
            
            if formTwo.validate_on_submit():
                bool = False

                statement = join_rel_table.delete().where(join_rel_table.c.user_id==current_user.userId).where(join_rel_table.c.event_id==event.eventId)
                
                db.session.execute(statement)
                db.session.commit()

                return redirect(url_for("event", event_id=event.eventId))
            
            return render_template("event.html", title=event.eventName, event=event, formOneOrTwo=formTwo, formButtonClass="danger", homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", reviewbody=reviewbody, reviews=reviews, category=category)

        else:
            formOne = JoinEventForm()

            if formOne.validate_on_submit():
                statement = join_rel_table.insert().values(event_id=event.eventId, user_id=current_user.userId)

                db.session.execute(statement)
                db.session.commit()

                return redirect(url_for("event", event_id=event.eventId))

            return render_template("event.html", title=event.eventName, event=event, formOneOrTwo=formOne, formButtonClass="warning", homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", reviewbody=reviewbody, reviews=reviews, category=category)

    return render_template("event.html", title=event.eventName, event=event, formThree=formThree, formFour=formFour, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", reviewbody=reviewbody, reviews=reviews, category=category)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", sender='noreply@demo.com', recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for("reset_token", token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is invalid or expired token.", "warning")
        return redirect(url_for("reset_request"))
    from = ResetPasswordForm()
    if formOne.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(formOne.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been update! You are now able to log in", "success")
        return redirect(url_for('login'))
    return render_template("reset_token.html", title="Reset Password", form=form)
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

@app.route("/home/eventpopulate=<int:eventsPage>", methods=["GET", "POST"])
@login_required
def populate_events(eventsPage):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    userFeedEvents = db.session.query(eventhascategory_rel_table, userhasinterest_rel_table, Events.eventName, Events.location, Events.eventId, Events.image_file, Events.eventDate, Events.eventStartTime, Events.eventEndTime, Events.host, Users.userId).filter(Users.userId==current_user.userId).filter(Events.eventId==eventhascategory_rel_table.c.event_id).filter(eventhascategory_rel_table.c.category_id==userhasinterest_rel_table.c.category_id).filter(userhasinterest_rel_table.c.user_id==current_user.userId).order_by(Events.dateCreated.desc()).paginate(page=eventsPage, per_page=2)

    eventList = []
    for c, event in enumerate(userFeedEvents.items):
        dict = {}
        
        dict["event_id"] = event.eventId
        dict["category_id"] = event.category_id
        dict["event_name"] = event.eventName
        dict["event_location"] = event.location
        dict["event_imgFile"] = event.image_file
        dict["event_date_dayNum"] = event.eventDate.strftime("%d")
        dict["event_date_dayName"] = event.eventDate.strftime("%a")
        dict["event_date_month"] = event.eventDate.strftime("%b")
        dict["event_startTime"] = event.eventStartTime.strftime("%I %p")
        
        eventList.append(dict)

    for x, event in enumerate(eventList):
        selectEvent = Events.query.filter_by(eventId=event["event_id"]).first()

        event["host_id"] = selectEvent.host.userId
        event["host_username"] = selectEvent.host.username
        event["host_firstName"] = selectEvent.host.firstName
        event["host_lastName"] = selectEvent.host.lastName

        joined = db.session.query(join_rel_table).filter(join_rel_table.c.user_id==current_user.userId, join_rel_table.c.event_id==event["event_id"]).first()
    
        if joined:
            event["joined"] = "True"

    return jsonify({"events" : eventList})

@app.route('/', methods=["GET","POST"])
@app.route('/home', methods=["GET","POST"])
def home():
    if current_user.is_authenticated:
        formTwo = CreateEventForm()
        
        if current_user.numberOfLogins == 0:
            return redirect(url_for("setup_acc"))

        eventBatchPage = request.args.get("page", 1, type=int)
        userFeedEvents = db.session.query(eventhascategory_rel_table, userhasinterest_rel_table, Events.eventName, Events.location, Events.eventId, Events.image_file, Events.eventDate, Events.eventStartTime, Events.eventEndTime, Events.host, Users.userId).filter(Users.userId==current_user.userId).filter(Events.eventId==eventhascategory_rel_table.c.event_id).filter(eventhascategory_rel_table.c.category_id==userhasinterest_rel_table.c.category_id).filter(userhasinterest_rel_table.c.user_id==current_user.userId).order_by(Events.dateCreated.desc()).paginate(page=eventBatchPage, per_page=2)

        display = []
        for c, event in enumerate(userFeedEvents.items):
            dict = {}
            
            dict["event_id"] = event.eventId
            dict["category_id"] = event.category_id
            dict["event_name"] = event.eventName
            dict["event_location"] = event.location
            dict["event_imgFile"] = event.image_file
            dict["event_date_dayNum"] = event.eventDate.strftime("%d")
            dict["event_date_dayName"] = event.eventDate.strftime("%a")
            dict["event_date_month"] = event.eventDate.strftime("%b")
            dict["event_startTime"] = event.eventStartTime.strftime("%I %p")
            
            display.append(dict)

        for x, event in enumerate(display):
            selectEvent = Events.query.filter_by(eventId=event["event_id"]).first()

            event["host_id"] = selectEvent.host.userId
            event["host_username"] = selectEvent.host.username
            event["host_firstName"] = selectEvent.host.firstName
            event["host_lastName"] = selectEvent.host.lastName

            joined = db.session.query(join_rel_table).filter(join_rel_table.c.user_id==current_user.userId, join_rel_table.c.event_id==event["event_id"]).first()
        
            if joined:
                event["joined"] = "True"

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

@app.route('/signup/i/1', methods=['GET', 'POST'])
def signup1():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    formOne = BasicAccountInfoForm()
    
    formOne.username.data = "johndoe"
    formOne.email.data = "johndoe@demo.com"
    formOne.password.data = "temporary"
    formOne.confirm_password.data = "temporary"

    if formOne.validate_on_submit():
        return redirect(url_for("signup2", formFirstName=formOne.firstName.data, formLastName=formOne.lastName.data))

    return render_template('signup1.html', title='Sign Up', formOne=formOne)

@app.route('/signup/i/2/fname=<formFirstName>&lname=<formLastName>', methods=['GET', 'POST'])
def signup2(formFirstName, formLastName):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    formOne = BasicAccountInfoForm()

    formOne.firstName.data = formFirstName
    formOne.lastName.data = formLastName
    formOne.password.data = "temporary"
    formOne.confirm_password.data = "temporary"

    if formOne.validate_on_submit():
        return redirect(url_for("signup3", formFirstName=formOne.firstName.data, formLastName=formOne.lastName.data, formUsername=formOne.username.data, formEmail=formOne.email.data))

    return render_template('signup2.html', title='Sign Up', formOne=formOne)

@app.route('/signup/i/3/fname=<formFirstName>&lname=<formLastName>&username=<formUsername>&email=<formEmail>', methods=['GET', 'POST'])
def signup3(formFirstName, formLastName, formUsername, formEmail):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    formOne = BasicAccountInfoForm()

    formOne.firstName.data = formFirstName
    formOne.lastName.data = formLastName
    formOne.username.data = formUsername
    formOne.email.data = formEmail

    if formOne.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(formOne.password.data).decode('utf-8')

        user = Users(firstName=formOne.firstName.data, lastName=formOne.lastName.data, username=formOne.username.data, email= formOne.email.data, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('interests'))

    return render_template('signup3.html', title='Sign Up', formOne=formOne)

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

    return render_template('gettingstarted1.html', title='Getting Started', formOne=formOne, display=display, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")

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

        flash("Welcome to Hap!", "success")
        return redirect(url_for('home'))

    profilePic = url_for("static", filename="images/" + current_user.image_file)
    return render_template('gettingstarted2.html', title='Getting Started', formOne=formOne, profilePic=profilePic, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white")

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
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="2px #FFC000 solid;", userInterests=userInterests)
    else:
        user = Users.query.filter_by(username=username).first()
        if user:
            userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
            profilePic = url_for("static", filename="images/" + user.image_file_sm)
            events = Events.query.filter_by(user_id=user.userId).order_by(Events.dateCreated.desc())
            createdEventsCount = Events.query.filter_by(user_id=user.userId).count()
            joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=user.userId)).count()
            
            return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="2px #FFC000 solid;", userInterests=userInterests)
        
        elif user is None:
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
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="2px #FFC000 solid;", userInterests=userInterests)
    else:
        user = Users.query.filter_by(username=username).first()
        if user:
            userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
            profilePic = url_for("static", filename="images/" + user.image_file_sm)
            events = Events.query.filter_by(user_id=user.userId).order_by(Events.dateCreated.desc())
            createdEventsCount = Events.query.filter_by(user_id=user.userId).count()
            joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=user.userId)).count()
            
            return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarCreatedEventsUnderline="2px #FFC000 solid;", userInterests=userInterests)

        elif user is None:
            return redirect(url_for("home"))

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
        return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="#FFC000", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarJoinedEventsUnderline="2px #FFC000 solid;", userInterests=userInterests)
    else:
        user = Users.query.filter_by(username=username).first()
        if user:
            userInterests = db.session.query(Categories.categoryName).filter(userhasinterest_rel_table.c.user_id==user.userId).filter(userhasinterest_rel_table.c.category_id==Categories.catId).all()
            profilePic = url_for("static", filename="images/" + user.image_file_sm)
            events = Events.query.filter(Events.joinrel.any(userId=user.userId)).order_by(Events.dateCreated.desc())
            createdEventsCount = Events.query.filter_by(user_id=user.userId).count()
            joinedEventsCount = Events.query.filter(Events.joinrel.any(userId=user.userId)).count()
            
            return render_template("account.html", title="Account", user=user, events=events, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", profilePic=profilePic, createdEventsCount=createdEventsCount, joinedEventsCount=joinedEventsCount, navbarJoinedEventsUnderline="2px #FFC000 solid;", userInterests=userInterests)

        elif user is None:
            return redirect(url_for("home"))

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
    return render_template("settings1.html", title="Settings", formOne=formOne, leftPanelItems=leftPanelItems, profilePic=profilePic, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", itemUnderline="underline;")

@app.route("/settings/security", methods=["GET", "POST"])
@login_required
def security_settings():
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    leftPanelItems = [['user.svg','acc_info_settings','Account Information'],['key.svg','security_settings','Security'],['controls.svg','interest_pref_settings','Interest Preferences']]

    return render_template("settings2.html", title="Settings", leftPanelItems=leftPanelItems, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", itemUnderline="underline;")

@app.route("/settings/interestpreferences", methods=["GET", "POST"])
@login_required
def interest_pref_settings():
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    leftPanelItems = [['user.svg','acc_info_settings','Account Information'],['key.svg','security_settings','Security'],['controls.svg','interest_pref_settings','Interest Preferences']]
    
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
        flash("Categories followed successfully.", "success")

        return redirect(url_for("acc_info_settings"))

    return render_template("settings3.html", title="Settings", formOne=formOne, display=display, leftPanelItems=leftPanelItems, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", itemUnderline="underline;")

@app.route("/event/<int:event_id>/bottomblockaction=bb1/page=<int:joinersPage>", methods=["GET", "POST"])
@login_required
def event_joiners(event_id, joinersPage):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    event = Events.query.get_or_404(event_id)

    joiners = db.session.query(Users.userId, Users.username, Users.image_file_sm, Users.firstName, Users.lastName, join_rel_table.c.dateJoined).filter(join_rel_table.c.event_id==event_id).filter(join_rel_table.c.user_id==Users.userId).order_by(join_rel_table.c.dateJoined.desc()).paginate(page=joinersPage, per_page=5)

    joinerList = []

    for joiner in joiners.items:
        joinerObj = {}

        joinerObj["userId"] = joiner.userId
        joinerObj["username"] = joiner.username
        joinerObj["image_file_sm"] = joiner.image_file_sm
        joinerObj["firstName"] = joiner.firstName
        joinerObj["lastName"] = joiner.lastName
        joinerObj["dateJoined"] = joiner.dateJoined
        
        joinerList.append(joinerObj)  

    return jsonify({"joiners" : joinerList})

@app.route("/event/<int:event_id>/bottomblockaction=bb<int:bottomBlock>", methods=["GET", "POST"])
@login_required
def event(event_id, bottomBlock):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    # eventPage = request.args.get('page', 1, type=int)
    # event = Events.query.get_or_404(event_id).paginate(page=eventPage, per_page=5)
    event = Events.query.get_or_404(event_id)
    eventCategory = Categories.query.filter(Categories.eventhascategory.any(eventId=event_id)).first()

    joinersPage = request.args.get("page", 1, type=int) 
    joinerProfPics = db.session.query(Users.username, Users.image_file_sm).filter(join_rel_table.c.event_id==event_id).filter(join_rel_table.c.user_id==Users.userId).order_by(join_rel_table.c.dateJoined.desc()).limit(11).all()
    joiners = db.session.query(Users.userId, Users.username, Users.image_file_sm, Users.firstName, Users.lastName, join_rel_table.c.dateJoined).filter(join_rel_table.c.event_id==event_id).filter(join_rel_table.c.user_id==Users.userId).order_by(join_rel_table.c.dateJoined.desc()).paginate(page=joinersPage, per_page=5)

    reviewPosts = db.session.query(review_rel_table.c.review, review_rel_table.c.dateReviewed, Users.firstName, Users.lastName, Users.image_file_sm, Users.username).filter(review_rel_table.c.event_id == event.eventId).filter(Users.userId == review_rel_table.c.user_id).order_by(review_rel_table.c.dateReviewed.desc()).all()
    ratingPosts = db.session.query(rate_rel_table.c.rate, rate_rel_table.c.dateRated, Users.firstName, Users.lastName, Users.image_file_sm, Users.username).filter(rate_rel_table.c.event_id == event.eventId).filter(Users.userId == rate_rel_table.c.user_id).order_by(rate_rel_table.c.dateRated.desc()).all()

    if event.host != current_user:
        formOne = PostReviewForm()
        formTwo = PostRateForm()
        formThree = UpdateRateForm()

        joinedEvent = db.session.query(join_rel_table).filter(join_rel_table.c.user_id==current_user.userId, join_rel_table.c.event_id==event.eventId).first()
        ratedEvent = db.session.query(rate_rel_table.c.rate).filter(rate_rel_table.c.user_id==current_user.userId, rate_rel_table.c.event_id==event.eventId).first()
        if ratedEvent:
            formThree.rating.default = ratedEvent.rate
            formThree.process() 

        return render_template("event.html", title=event.eventName, event=event, formOne=formOne, formTwo=formTwo, formThree=formThree, joinedEvent=joinedEvent, ratedEvent=ratedEvent, joiners=joiners, joinerProfPics=joinerProfPics, reviewPosts=reviewPosts, ratingPosts=ratingPosts, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", eventCategory=eventCategory, bottomBlock=bottomBlock)

    else:
        formTwo = DeleteEventForm()
        formThree = UpdateEventForm()
        formTwo.eventName.data = event.eventName

        if formTwo.validate_on_submit():
            statement = review_rel_table.delete().where(review_rel_table.c.event_id==event.eventId)
                
            db.session.execute(statement)
            db.session.delete(event)
            db.session.commit()
            flash("Your event has been deleted.", "success")

            return redirect(url_for('home'))
        
        elif formTwo.confirm_eventName.data:
            flash("Your event has been deleted.", "danger")

            return redirect(url_for('event', event_id=event.eventId, bottomBlock=1))

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

            flash("Your event has been updated.", "success")

            return redirect(url_for('event', event_id=event.eventId, bottomBlock=1))

        if request.method == "GET":
            formThree.eventName.data = event.eventName
            formThree.eventDescription.data = event.eventDescription
            formThree.eventDate.data = event.eventDate
            formThree.startTime.data = event.eventStartTime
            formThree.endTime.data = event.eventEndTime
            formThree.fee.data = event.fee
            formThree.location.data = event.location

        return render_template("event.html", title=event.eventName, event=event, formThree=formThree, formTwo=formTwo, joiners=joiners, joinerProfPics=joinerProfPics, reviewPosts=reviewPosts, ratingPosts=ratingPosts, homeNavbarLogoBorderBottom="white", profileNavbarLogoBorderBottom="white", eventCategory=eventCategory, bottomBlock=bottomBlock)

@app.route("/event/<int:event_id>/bottomblockaction=bb<int:bottomBlock>/join", methods=["GET", "POST"])
@login_required
def join_event(event_id, bottomBlock):
    if request.method == 'GET':
        if current_user.numberOfLogins == 0:
            return redirect(url_for("setup_acc"))

        return redirect(url_for("event", event_id=event_id, bottomBlock=1))

    elif request.method == 'POST': 
        req = request.form['event_id']

        lookRow = db.session.query(join_rel_table).filter(join_rel_table.c.user_id==current_user.userId, join_rel_table.c.event_id==req).first()

        if lookRow is None:
            statement =  join_rel_table.insert().values(user_id=current_user.userId, event_id=req)

            db.session.execute(statement)
            db.session.commit()

        return jsonify({'result' : 'success'})

@app.route("/event/<int:event_id>/bottomblockaction=bb<int:bottomBlock>/unjoin", methods=["GET", "POST"])
@login_required
def unjoin_event(event_id, bottomBlock):
    if request.method == 'GET':
        if current_user.numberOfLogins == 0:
            return redirect(url_for("setup_acc"))
        
        return redirect(url_for("event", event_id=event_id, bottomBlock=bottomBlock))

    elif request.method == 'POST': 
        statement = join_rel_table.delete().where(join_rel_table.c.user_id==current_user.userId).where(join_rel_table.c.event_id==request.form['event_id'])
                    
        db.session.execute(statement)
        db.session.commit()

        return jsonify({'result' : 'success'})

@app.route("/event/<int:event_id>/review", methods=["GET", "POST"])
@login_required
def review_event(event_id):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    event = Events.query.get_or_404(event_id)

    if request.method == 'GET':
        if current_user.numberOfLogins == 0:
            return redirect(url_for("setup_acc"))
        
        return redirect(url_for("event", event_id=event.eventId, bottomBlock=2))

    if request.method == 'POST':
        formOne = PostReviewForm()

        if formOne.review.data:
            statement = review_rel_table.insert().values(user_id=current_user.userId, event_id=event.eventId, review=formOne.review.data)
            
            db.session.execute(statement)
            db.session.commit()

            return redirect(url_for("event", event_id=event_id, bottomBlock=2))

@app.route("/event/<int:event_id>/rate", methods=["GET", "POST"])
@login_required
def rate_event(event_id):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    event = Events.query.get_or_404(event_id)

    if request.method == 'GET':
        if current_user.numberOfLogins == 0:
            return redirect(url_for("setup_acc"))
        
        return redirect(url_for("event", event_id=event.eventId, bottomBlock=3))

    if request.method == 'POST':
        eventReq = request.form['event_id']
        rateReq = request.form['rate']

        statement = rate_rel_table.insert().values(user_id=current_user.userId, event_id=eventReq, rate=rateReq)
        
        db.session.execute(statement)
        db.session.commit()

        return redirect(url_for("event", event_id=event_id, bottomBlock=3))

@app.route("/event/<int:event_id>/updaterate", methods=["GET", "POST"])
@login_required
def update_rate_event(event_id):
    if current_user.numberOfLogins == 0:
        return redirect(url_for("setup_acc"))

    event = Events.query.get_or_404(event_id)

    if request.method == 'GET':
        if current_user.numberOfLogins == 0:
            return redirect(url_for("setup_acc"))
        
        return redirect(url_for("event", event_id=event.eventId, bottomBlock=3))

    if request.method == 'POST':
        eventReq = request.form['event_id']
        rateReq = request.form['rate']

        statementOne = rate_rel_table.delete().where(rate_rel_table.c.user_id==current_user.userId).where(rate_rel_table.c.event_id==eventReq)
        statementTwo = rate_rel_table.insert().values(user_id=current_user.userId, event_id=eventReq, rate=rateReq)

        db.session.execute(statementOne)
        db.session.execute(statementTwo)
        db.session.commit()

        return redirect(url_for("event", event_id=event_id, bottomBlock=3))

def send_reset_email(userId):
    token = userId.get_reset_token()
    msg = Message("Password Reset Request", sender="noreply@demo.com", recipients=[userId.email])
    # msg.body = f'''To reset your password, visit the following link: {url_for('reset_token', token=token, _external=True)}. If you did not make this request then simply ignore, Thank You.'''
    # msg.body = "To reset your password, visit the following link: {url_for('{}', token=token, _external=True)}. If you did not make this request then simply ignore, Thank You.".format('reset_token')
    msg.body = '''To reset your password, visit the following link:
{}.

If you did not make this request then simply ignore, Thank You.
    '''.format(url_for('reset_token', token=token, _external=True))

    mail.send(msg)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for("login"))
    return render_template("resetrequest.html", title="Reset Password", form=form)

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = Users.verify_reset_token(token)
    if user is None:
        flash("That is invalid or expired token.", "warning")
        return redirect(url_for('resetrequest'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been update! You are now able to log in", "success")
        return redirect(url_for('login'))
    return render_template("resettoken.html", title="Reset Password", form=form)

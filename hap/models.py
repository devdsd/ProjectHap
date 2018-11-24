from datetime import datetime
from hap import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

review_rel_table = db.Table('review_rel_table',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
    db.Column('review', db.Text, nullable=True)
)

rate_rel_table = db.Table('rate_rel_table',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
    db.Column('rate', db.Integer)
)

join_rel_table = db.Table('join_rel_table',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'))
)

userhasinterest_rel_table = db.Table('userhasinterest_rel_table',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
)

eventhascategory_rel_table = db.Table('eventhascategory_rel_table',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
)

   
class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "{}".format(self.categoryName)
        # return "Categories({})".format(self.categoryName)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    creates = db.relationship('Events', backref='host', lazy=True)
    image_file = db.Column(db.String(50), nullable=False, default='default-profPic.jpg')
    image_file_sm = db.Column(db.String(50), nullable=False, default='default-profPic-sm.jpg')
    review_relationship = db.relationship('Events', secondary=review_rel_table, backref=db.backref('reviewrel', lazy=True))
    rate_relationship = db.relationship('Events', secondary=rate_rel_table, backref=db.backref('raterel', lazy=True))
    userhasinterest_relationship = db.relationship('Categories', secondary=userhasinterest_rel_table, backref=db.backref('userhasinterest', lazy=True))
    join_relationship = db.relationship('Events', secondary=join_rel_table, backref=db.backref('joinrel', lazy=True))

    def __repr__(self):
        return "Users({}, {}, {}, {}, {})".format(self.firstName, self.lastName, self.email, self.username, self.interest)

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventName = db.Column(db.String(100), nullable=False)
    dateCreated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    eventDate = db.Column(db.DateTime, nullable=False)
    eventStartTime = db.Column(db.Time)
    eventEndTime = db.Column(db.Time)
    eventDescription = db.Column(db.Text, nullable=True)
    location = db.Column(db.Text, nullable=False)
    fee = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='default-eventBanner.jpg')
    image_file_sm = db.Column(db.String(50), nullable=False, default='default-eventBanner-sm.jpg')
    eventhascategory_relationship = db.relationship('Categories', secondary=eventhascategory_rel_table, backref=db.backref('eventhascategory', lazy=True))

    def __repr__(self):
        return "Events({}, {}, {}, {}, {}, {}, {})".format(self.eventName, self.location, self.eventDate, self.eventStartTime, self.eventEndTime, self.eventDescription, self.fee)
 

# def categories_query():
#     return Categories.query
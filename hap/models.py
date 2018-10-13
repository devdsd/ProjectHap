from datetime import datetime
from hap import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

review = db.Table('review',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'))
)

rate = db.Table('')

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    creates = db.relationship('Events', backref='host', lazy=True)
    reviews = db.relationship('Events', secondary=review, backref=db.backref('reviewers', lazy=True))

    def __repr__(self):
        return "Users({}, {}, {}, {}, {})".format(self.firstName, self.lastName, self.email, self.username)

		
class Events(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	eventName = db.Column(db.String(100), nullable=False)
    eventDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    eventDescription = db.Column(db.Text, nullable=True)
    fee = db.Column(db.Integer, default="0")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "Events({}, {}, {}, {})".format(self.eventName, self.eventDate, self.eventDescription, self.fee)

class Categories(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "Categories({})".format(self.categoryName)


class Venues(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    barangay = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "Venues({}, {})".format(self.barangay, self.town)
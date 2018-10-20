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
    db.Column('rate', db.Text, nullable=True)
)

join_rel_table = db.Table('join_rel_table',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'))
)



class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    creates = db.relationship('Events', backref='host', lazy=True)
    review_relationship = db.relationship('Events', secondary=review_rel_table, backref=db.backref('reviewrel', lazy=True))
    rate_relationship = db.relationship('Events', secondary=rate_rel_table, backref=db.backref('raterel', lazy=True))

    def __repr__(self):
        return "Users({}, {}, {}, {})".format(self.firstName, self.lastName, self.email, self.username)

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventName = db.Column(db.String(100), nullable=False)
    dateCreated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    eventDate = db.Column(db.DateTime, nullable=False)
    eventDescription = db.Column(db.Text, nullable=True)
    location = db.Column(db.Text, nullable=False)
    fee = db.Column(db.Integer, default="0")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "Events({}, {}, {}, {})".format(self.eventName, self.eventDate, self.eventDescription, self.fee)
    


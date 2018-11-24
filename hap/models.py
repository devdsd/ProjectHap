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

# userhasinterest_rel_table = db.Table('userhasinterest_rel_table',
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#     db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
# )

# eventhascategory_rel_table = db.Table('eventhascategory_rel_table',
#     db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
#     db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
# )

# eventhasvenue_rel_table = db.Table('eventhasvenue_rel_table',
#     db.Column('event_id', db.Integer, db.ForeignKey('events.id')),
#     db.Column('venue_id', db,Integer, db.ForeignKey('venues.id'))
# )

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default = 'default-image.png')
    password = db.Column(db.String(60), nullable=False)
    creates = db.relationship('Events', backref='host', lazy=True)
    review_relationship = db.relationship('Events', secondary=review_rel_table, backref=db.backref('reviewrel', lazy=True))
    rate_relationship = db.relationship('Events', secondary=rate_rel_table, backref=db.backref('raterel', lazy=True))
    # userhasinterest_relationship = db.relationship('Categories', secondary=userhasinterest_rel_table, backref=db.backref('userhasinterestrel', lazy=True))

    def __repr__(self):
        return "Users({}, {}, {}, {})".format(self.firstName, self.lastName, self.email, self.username)

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventName = db.Column(db.String(100), nullable=False)
    eventDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    eventDescription = db.Column(db.Text, nullable=True)
    fee = db.Column(db.Integer, default="0")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # eventhascategory_relationship = db.relationship('Categories', secondary=eventhascategory_rel_table, backref=db.backref('eventhascategoryrel', lazy=True))
    # eventhasvenue_relationship = db.relationship('Venues', backref='eventhasvenuerel', lazy=True)

    def __repr__(self):
        return "Events({}, {}, {}, {})".format(self.eventName, self.eventDate, self.eventDescription, self.fee)
    
        

# class Venues(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     barangay = db.Column(db.String(50), nullable=False)
#     town = db.Column(db.String(50), nullable=False)
#     event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)


#     def __repr__(self):
#         return "Venues({}, {})".format(self.barangay, self.town)

# class Categories(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     categoryName = db.Column(db.String(100), nullable=False)

#     def __repr__(self):
#         return "Categories({})".format(self.categoryName)


# # class Images(db.Model):
# #     id = db.Column

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(2000))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='title', lazy='dynamic')

    def get_comments(self):
        return Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc())


    def __repr__(self):
        return '<Post %r>' % (self.body)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

        
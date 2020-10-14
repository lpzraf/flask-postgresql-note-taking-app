from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# testing association table
followers = db.Table('followers', db.Column('follower_id', db.Integer,
                     db.ForeignKey('users.id')), db.Column('followed_id',
                     db.Integer, db.ForeignKey('users.id')))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(120), unique=True)
    date = db.Column(db.DateTime)
    notes = db.relationship(
        'Note',
        backref='user',
        lazy='dynamic',
        cascade="all, delete")
    # testing many-to-many
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __init__(self, username, password, date):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.date = date

    def __repr__(self):
        return '<User %r>' % self.username

    @classmethod
    def authenticate(cls, username, password):
        found_user = cls.query.filter_by(username=username).first()
        if found_user:
            authenticated_user = bcrypt.check_password_hash(
                found_user.password,
                password)
            if authenticated_user:
                return found_user
        return False

    # testing add and remove relationships
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_notes(self):
        return Note.query.join(
            followers, (followers.c.followed_id == Note.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Note.date.desc())


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime)
    note_body = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title, date, note_body, user_id):
        self.title = title
        self.date = date
        self.note_body = note_body
        self.user_id = user_id

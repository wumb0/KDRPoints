from app import db
from config import USER_ROLES

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), index = True)
    email = db.Column(db.String(100), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = USER_ROLES['user'])
    postition = db.Column(db.String(50), index = True)
    pin = db.Column(db.Integer, index=True, unique = True)
    last_seen = db.Column(db.DateTime)
    points = db.relationship('Points', backref = 'user', lazy = 'dynamic')
    awards = db.relationship('Award', backref = 'user', lazy = 'dynamic')

    def is_admin(self):
        if self.role is USER_ROLES['admin']:
            return True
        return False

    def is_chair(self):
        if self.role is USER_ROLES['chair']:
            return True
        return False

    def __repr__(self):
        return '<User {}'.format(self.name)

class Points(db.Model):
    id = db.Column(db.Integer, primary_key = True)

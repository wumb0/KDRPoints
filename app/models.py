from app import db
from config import USER_ROLES

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), index = True)
    nickname = db.Column(db.String(50), index = True)
    email = db.Column(db.String(100), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = USER_ROLES['user'])
    postition = db.Column(db.String(50), index = True)
    pin = db.Column(db.Integer, index = True, unique = True)
    last_seen = db.Column(db.DateTime)
    active = db.Column(db.Boolean)
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

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User {}'.format(self.name)

    def last_seen(self):
        return self.last_seen.strftime('%A, %B %d %Y %I:%M%p')

    def get_points(self, semester, event='all'):
        total = 0
        for p in self.points:
            if p.semester is semester:
                if event is 'all':
                    total += p.amount
                elif p.event is event:
                    total += p.amount
        return total

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.Integer, index = True)
    season = db.Column(db.String(20), index = True)
    current = db.Column(db.Boolean, default = False)

    def get_name(self):
        return "{} {}".format(self.season, self.year)

    def get_linkname(self):
        return "{}{}".format(self.season, self.year)

    def __repr__(self):
        return '<Semester: {} {}>'.format(self.season, self.year)

    def __cmp__(self, other):
        try:
            if self.id == other.id:
                return 0
            if self.id > other.id:
                return 1
            if self.id < other.id:
                return -1
        except:
            return -1

class Points(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))

    def __repr__(self):
        return '<Points: {} | {} | {}>'.format(self.user_id, self.event_id, self.amount)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    event_picker = db.Column(db.Boolean)
    name = db.Column(db.String(50), index = True)
    description = db.Column(db.String(1000))
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    date = db.Column(db.DateTime)
    points = db.relationship('Points', backref = 'event', lazy = 'dynamic')

    def __repr__(self):
        return '<Event: {}>'.format(self.name)

    def __cmp__(self, other):
        try:
            if self.id == other.id:
                return 0
            if self.id > other.id:
                return 1
            if self.id < other.id:
                return -1
        except:
            return -1

class Award(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), index = True)
    icon = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return 'Award: {}'.format(self.name)

from app import db
from config import USER_ROLES
from datetime import datetime

events = db.Table('events',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('brother_id', db.Integer, db.ForeignKey('brother.id'))
)

awards = db.Table('awards',
    db.Column('award_id', db.Integer, db.ForeignKey('award.id')),
    db.Column('brother_id', db.Integer, db.ForeignKey('brother.id'))
)

class Brother(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), index = True)
    nickname = db.Column(db.String(50), index = True)
    email = db.Column(db.String(100), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = USER_ROLES['user'])
    position = db.Column(db.String(50), index = True)
    pin = db.Column(db.Integer, index = True)
    last_seen = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default = True)
    points = db.relationship('OtherPoints', backref = 'brother', lazy = 'dynamic')
    awards = db.relationship('Award', secondary=awards, backref = 'brothers', lazy = 'dynamic')
    events = db.relationship('Event', secondary=events, backref='brothers', lazy='dynamic')
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    family = db.relationship('Family', backref="brothers")

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

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return self.name

    def last_seen(self):
        return self.last_seen.strftime('%A, %B %d %Y %I:%M%p')

    def get_all_points(self, semester):
        total = 0
        for p in self.points:
            if p.semester is semester:
                    total += p.points
        for e in self.events:
            if e.semester is semester:
                total += e.points
        for a in self.awards:
            if a.semester is semester:
                total += a.points
        return total

class Family(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(15))

    def get_points(self, semester):
        total = 0
        for b in self.brothers:
            total += b.get_all_points(semester)
        return total

    def __repr__(self):
        return self.name

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.Integer, index = True, )
    season = db.Column(db.String(20), index = True)
    current = db.Column(db.Boolean, default = False)

    def get_name(self):
        return "{} {}".format(self.season, self.year)

    def get_linkname(self):
        return "{}{}".format(self.season, self.year)

    def __repr__(self):
        return '{} {}'.format(self.season, self.year)

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

class OtherPoints(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    brother_id = db.Column(db.Integer, db.ForeignKey('brother.id'))
    points = db.Column(db.Integer)
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    reason = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '{} Points'.format(self.amount)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    event_picker = db.Column(db.Boolean, default = True)
    name = db.Column(db.String(50), index = True)
    description = db.Column(db.String(1000))
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    date = db.Column(db.Date, default=datetime.today)
    points = db.Column(db.Integer, default = 0)

    def __repr__(self):
        return self.name

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
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    points = db.Column(db.Integer, default = 0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.name

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

points = db.Table('points',
    db.Column('otherpoints_id', db.Integer, db.ForeignKey('otherpoints.id')),
    db.Column('brother_id', db.Integer, db.ForeignKey('brother.id'))
)

class Brother(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), index = True)
    nickname = db.Column(db.String(50), index = True)
    email = db.Column(db.String(100), index = True, unique = True, nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))
    position = db.relationship('Position', backref = "brothers")
    pin = db.Column(db.Integer, index = True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    active = db.Column(db.Boolean, default = True, nullable=False)
    points = db.relationship('OtherPoints', secondary=points, backref = 'brothers', lazy = 'dynamic')
    awards = db.relationship('Award', secondary=awards, backref = 'brothers', lazy = 'dynamic')
    events = db.relationship('Event', secondary=events, backref='brothers', lazy='dynamic')
    service = db.relationship('Service')
    studyhours = db.relationship('StudyHours')
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    family = db.relationship('Family', backref="brothers")

    def is_admin(self):
        if self.position is None:
            return False
        if self.position.permission == USER_ROLES['admin']:
            return True
        return False

    def is_chair(self):
        if self.position is None:
            return False
        if self.position.permission == USER_ROLES['chair']:
            return True
        return False

    def is_normal_user(self):
        if self.position is None:
            return True
        if self.position.permission == USER_ROLES['user']:
            return True
        return False

    def is_service_chair(self):
        if self.position is None:
            return False
        if "service" in self.position.name.lower():
            return True

    def total_service_hours(self, semester):
        total = 0
        for serv in self.service:
            if serv.semester == semester and serv.approved is True:
                total += ((serv.end - serv.start).seconds/3600.0)*float(serv.weight)
        return total

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Brother: {}>".format(self.name)

    def last_seen_print(self):
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
    name = db.Column(db.String(15), nullable=False)

    def get_points(self, semester):
        total = 0
        for b in self.brothers:
            total += b.get_all_points(semester)
        if len(self.brothers) != 0:
            return total/len(self.brothers)
        else:
            return 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Family: {}>".format(self.name)

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.Integer, index = True, nullable=False)
    season = db.Column(db.String(20), index = True, nullable=False )
    current = db.Column(db.Boolean, default = False, nullable=False )
    linkname = db.Column(db.String(20))

    def get_name(self):
        return "{} {}".format(self.season, self.year)

    def __str__(self):
        return '{}'.format(self.get_name())

    def __repr__(self):
        return "<Semester: {}>".format(self.get_name())

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
    __tablename__ = 'otherpoints'
    id = db.Column(db.Integer, primary_key = True)
    points = db.Column(db.Integer, nullable=False)
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    def __str__(self):
        return '{} Points'.format(self.amount)

    def __repr__(self):
        return "<Points: {} - {} {}>".format(self.reason, self.semester.get_name())

    def print_timestamp(self):
        return self.timestamp.strftime('%A, %B %d %Y %I:%M%p')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    event_picker = db.Column(db.Boolean, default = True, nullable=False)
    code_enable = db.Column(db.Boolean, default = False, nullable=False)
    code = db.Column(db.String(10), default="0000", nullable=False)
    name = db.Column(db.String(50), index = True, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.today, nullable=False)
    points = db.Column(db.Integer, default = 0, nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Event: {} - {} {}>".format(self.name, self.semester.get_name())

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

    def print_timestamp(self):
        return self.timestamp.strftime('%A, %B %d %Y %I:%M%p')

class Award(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), index = True, nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    points = db.Column(db.Integer, default = 0, nullable=False )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    color = db.Column(db.String(15), default="000000", nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Award: {} - {}>".format(self.name, self.semester.get_name())

    def print_timestamp(self):
        return self.timestamp.strftime('%A, %B %d %Y %I:%M%p')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), index = True, nullable=False)
    info = db.Column(db.String(200))
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    brother_id = db.Column(db.Integer, db.ForeignKey('brother.id'), nullable=False)
    brother = db.relationship("Brother")
    approved = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    weight = db.Column(db.Float, default=1.0, nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Service: {} - {}>".format(self.name, self.semester.get_name())

class StudyHours(db.Model):
    __tablename__ = 'studyhours'
    id = db.Column(db.Integer, primary_key = True)
    info = db.Column(db.String(200), nullable = False)
    semester = db.relationship("Semester")
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    brother_id = db.Column(db.Integer, db.ForeignKey('brother.id'), nullable=False)
    brother = db.relationship("Brother")
    approved = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.info

    def __repr__(self):
        return "<Study hours: {} - {}>".format(self.semester.get_name(), self.brother.name)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    permission = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return "<{}>".format(self.name)

    def __str__(self):
        return self.name

from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, SelectField, IntegerField, widgets, HiddenField, BooleanField, DateTimeField, SelectMultipleField
from wtforms.fields import TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange
from datetime import datetime, timedelta
from app.models import *
#from config import USER_ROLES

class FirstLoginForm(Form):
    name = TextField('Name', validators = [DataRequired(), Length(max=50)])
    nickname = TextField('Nickname', validators=[Length(max=50)])
    pin = IntegerField('Pin', validators = [DataRequired(), NumberRange(min=1, max=2000)])
    active = BooleanField('Active', default=True)
    families = [(x.id, x.name) for x in Family.query.all()]
    family = SelectField('Family Line', choices = families, coerce=int)
    submit = SubmitField('submit')

    def validate(self):
        if not Form.validate(self):
            return False
        return True

    def validate_pin(self, field):
        if not isinstance(self.pin.data, int) or self.pin.data <= 0:
                raise ValidationError("The PIN number entered was invalid")
        if Brother.query.filter_by(pin=self.pin.data).first() is not None:
                raise ValidationError("The PIN number entered has already been taken")

class AttendForm(Form):
    event = SelectField('Event', choices=[], coerce=int)
    pin = IntegerField('Pin', validators=[DataRequired()], default="")
    code = TextField('Code', default="0000", validators=[Length(max=10)])
    submit = SubmitField('submit')

    def validate(self):
        if not Form.validate(self):
            return False
        return True

    def validate_pin(self, field):
        if self.pin.data <= 0:
            raise ValidationError("Invalid PIN entered")
        if not self.pin.data in [ x.pin for x in Brother.query.all() ]:
            raise ValidationError("The PIN number does not exist in the database")

class EditNickForm(Form):
    nickname = TextField("New Nickname", validators=[Length(max=50)])
    submit = SubmitField('submit')

    def validate(self):
        if not Form.validate(self):
            return False
        return True

def roundTime():
    tm = datetime.now()
    tm = tm - timedelta(minutes=tm.minute % 15,
                                seconds=tm.second,
                                microseconds=tm.microsecond)
    return tm

class ServiceForm(Form):
    name = TextField('Event Name', validators=[DataRequired(), Length(max=50)])
    start = DateTimeField('Start Time', validators=[DataRequired()], format='%m/%d/%Y %I:%M %p', default=roundTime())
    end = DateTimeField('End Time', validators=[DataRequired()], format='%m/%d/%Y %I:%M %p', default=roundTime())
    info = TextAreaField('Additional info')
    submit = SubmitField('submit')

    def validate(self):
        if not Form.validate(self):
            return False
        return True

    def validate_end(self, field):
        if self.end.data <= self.start.data:
            raise ValidationError("The end must be after the beginning")


class Randomizer(Form):
    number = TextField("Number of Brothers", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Go!')


class MassAttendForm(Form):
    brothers = [ (x.id, x.name) for x in sorted(Brother.query.filter_by(active=True), key=lambda x: x.name) ]
    event = SelectField('Event', choices=[], coerce=int)
    brothers = SelectMultipleField("Brothers", choices=brothers, coerce=int, option_widget=widgets.CheckboxInput())
    submit = SubmitField("Attend")

    def validate(self): #brothers field fails check because object, just work around for now
        return True

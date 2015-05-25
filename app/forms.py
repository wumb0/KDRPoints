from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, SelectField, IntegerField, widgets, HiddenField, BooleanField, DateTimeField
from wtforms.fields import TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange
from datetime import datetime, timedelta
from app.models import *
#from config import USER_ROLES

class FirstLoginForm(Form):
    name = TextField('name', validators = [DataRequired(), Length(max=50)])
    nickname = TextField('nickname', validators=[Length(max=50)])
    pin = IntegerField('pin', validators = [DataRequired(), NumberRange(min=1, max=2000)])
    active = BooleanField('active', default=True)
    families = [(x.id, x.name) for x in Family.query.all()]
    family = SelectField('family', choices = families, coerce=int)
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
    event = SelectField('event', choices=[], coerce=int)
    pin = IntegerField('pin', validators=[DataRequired()], default="")
    code = TextField('code', default="0000", validators=[Length(max=10)])
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
    nickname = TextField("nickname", validators=[Length(max=50)])
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
    name = TextField('name', validators=[DataRequired(), Length(max=50)])
    start = DateTimeField('start', validators=[DataRequired()], format='%m/%d/%Y %I:%M %p', default=roundTime())
    end = DateTimeField('end', validators=[DataRequired()], format='%m/%d/%Y %I:%M %p', default=roundTime())
    info = TextAreaField('info')
    submit = SubmitField('submit')

    def validate(self):
        if not Form.validate(self):
            return False
        return True

    def validate_end(self, field):
        if self.end.data <= self.start.data:
            raise ValidationError("The end must be after the beginning")


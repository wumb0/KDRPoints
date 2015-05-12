from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, SelectField, IntegerField
#from wtforms.fields import TextAreaField
from wtforms.validators import DataRequired, ValidationError
from app.models import *
#from config import USER_ROLES

class FirstLoginForm(Form):
    name = TextField('name', validators = [DataRequired()])
    nickname = TextField('nickname')
    pin = IntegerField('pin', validators = [DataRequired()])
    families = [(x.id, x.name) for x in Family.query.all()]
    family = SelectField('family', choices = families, coerce=int)
    submit = SubmitField('submit')

    def validate(self):
        if not Form.validate(self):
            return False
        if not isinstance(self.pin.data, int) or self.pin.data <= 0:
                raise ValidationError("The PIN number entered was invalid")
                return False
        if Brother.query.filter_by(pin=self.pin.data).first() is not None:
                raise ValidationError("The PIN number entered has already been taken")
                return False
        return True

class AttendForm(Form):
    current_semester = Semester.query.filter_by(current=True).first()
    events = []
    events_query = Event.query.filter_by(event_picker=True, semester_id=current_semester.id).all()
    if events is not None:
        events = [ (x.id, x.name) for x in events_query ]
    event = SelectField('event', choices=events, coerce=int)
    pin = IntegerField('pin', validators=[DataRequired()])
    submit = SubmitField('submit')

    def validate(self):
        if not Form.validate(self):
            return False
        if not self.pin.data in [ x.pin for x in  Brothers.query.all() ]:
            return False
        return True

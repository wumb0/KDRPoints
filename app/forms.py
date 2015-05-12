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
    event = SelectField('event', choices=[], coerce=int)
    pin = IntegerField('pin', validators=[DataRequired()])
    submit = SubmitField('submit')

    def validate(self):
        if not Form.validate(self):
            return False
        if not self.pin.data in [ x.pin for x in Brother.query.all() ]:
            return False
        return True

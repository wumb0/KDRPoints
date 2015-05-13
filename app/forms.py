from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, SelectField, IntegerField, widgets, HiddenField
from wtforms.fields import TextAreaField
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
        return True

    def validate_pin(self, field):
        if not isinstance(self.pin.data, int) or self.pin.data <= 0:
                raise ValidationError("The PIN number entered was invalid")
        if Brother.query.filter_by(pin=self.pin.data).first() is not None:
                raise ValidationError("The PIN number entered has already been taken")

class AttendForm(Form):
    event = SelectField('event', choices=[], coerce=int)
    pin = IntegerField('pin', validators=[DataRequired()])
    code = HiddenField('code', validators=[DataRequired()], default="0000")
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

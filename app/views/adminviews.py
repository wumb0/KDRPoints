from app import db, models
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla.view import ModelView, func
from flask_login import current_user
from flask import redirect, url_for, flash, request
from config import USER_ROLES
from wtforms.validators import NumberRange
from app.email import send_email
from wtforms import SelectField
from datetime import datetime

class ProtectedBaseView(BaseView):
    def is_accessible(self):
        if current_user.is_authenticated and (not current_user.is_normal_user() or current_user.id == 1):
            return True
        return False

    def _handle_view(self, name, **kwargs):
            if not self.is_accessible():
                flash("You don't have permission to go there", category="warning")
                return redirect(url_for('main.index'))

class AdminBaseView(ProtectedBaseView):
    def is_visible(self):
        if current_user.is_authenticated and (current_user.is_admin() or current_user.id == 1):
            return True
        return False

    def is_accessible(self):
        if current_user.is_authenticated and (current_user.is_admin() or current_user.id == 1):
            return True
        return False

class ProtectedIndexView(AdminIndexView, ProtectedBaseView):
    pass

class ProtectedModelView(ModelView, ProtectedBaseView):
    column_display_actions = True

class AdminModelView(ModelView, AdminBaseView):
    column_display_actions = True

class ProtectedAdminIndex(ProtectedIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', user=current_user)

class BrotherModelView(AdminModelView):
    column_exclude_list = ['points']
    column_default_sort = ('active', True)
    can_create = False
    column_display_pk = True
    column_hide_backrefs = False
    form_excluded_columns = ('points', 'awards',
                             'events', 'studyhours',
                             'service', 'last_seen',
                             'email')

    def __init__(self, session):
        super(BrotherModelView, self).__init__(models.Brother, session)

class PositionModelView(AdminModelView):
    column_list = ('name', 'brothers', 'permission')
    column_choices = {'permission': [(0, 'User'), (1, 'Chair'), (2, 'Admin')]}
    choices = [ (int(USER_ROLES[i]), i) for i in USER_ROLES.keys() ]
    form_overrides = dict(permission=SelectField)
    form_args = dict(permission=dict(choices=choices,
                                     validators=[NumberRange(min=0, max=2)],
                                     coerce=int))

    def __init__(self, session):
        super(PositionModelView, self).__init__(models.Position, session)

class FamilyModelView(AdminModelView):
    can_create = False
    can_edit = False

    def __init__(self, session):
        super(FamilyModelView, self).__init__(models.Family, session)

class EventModelView(ProtectedModelView):
    column_default_sort = ('timestamp', True)
    form_excluded_columns = ['signupsheet']
    semester = models.Semester.query.filter_by(current=True).first()
    form_args = dict(points=dict(validators=[NumberRange(min=0)]),
                     semester=dict(default=semester),
                     brothers=dict(query_factory=
                                   lambda: models.Brother.query.filter_by(active=True)))

    def __init__(self, session):
        super(EventModelView, self).__init__(models.Event, session)

    def get_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(self.model).filter(self.model.semester==semester)

    def get_count_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(func.count('*')).filter(self.model.semester==semester)


class PointsModelView(ProtectedModelView):
    column_default_sort = ('timestamp', True)
    semester = models.Semester.query.filter_by(current=True).first()
    form_args = dict(points=dict(validators=[NumberRange(min=0)]),
                     semester=dict(default=semester),
                     brothers=dict(query_factory=
                                   lambda: models.Brother.query.filter_by(active=True)))

    def __init__(self, session):
        super(PointsModelView, self).__init__(models.OtherPoints, session)

    def get_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(self.model).filter(self.model.semester==semester)

    def get_count_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(func.count('*')).filter(self.model.semester==semester)

class SemesterModelView(AdminModelView):
    form_excluded_columns = ('linkname', 'signupsheets')
    column_default_sort = ('current', True)
    form_args = dict(year=dict(validators=[NumberRange(min=2014, max=2100)]))
    choices = [ (i, i) for i in ["Fall", "Spring"] ]
    form_overrides = dict(season=SelectField)
    form_args = dict(season=dict(choices=choices),
                     year=dict(default=datetime.utcnow().year))
    form_widget_args = {
        'required_service': {
            'style': "width: 5em;"
        },
        'year': {
            'style': "width: 7em;"
        },
        'season': {
            'style': "width: 7em;"
        }
    }

    def on_model_change(self, form, model, is_created):
        model.linkname = (model.season + str(model.year)).lower()
        db.session.add(model)
        if model.current:
            sems = model.query.filter_by(current=True)
            for sem in sems:
                if sem is not model:
                    sem.current = False
                    if not sem.ended:
                        sem.active_brothers = models.Brother.query.filter_by(active=True).all()
                    sem.ended = True
                    db.session.add(sem)
        db.session.commit()

    def __init__(self, session):
        super(SemesterModelView, self).__init__(models.Semester, session)

class AwardModelView(ProtectedModelView):
    form_args = dict(icon=dict(cols=5))
    form_widget_args = {
        'color': {
            'style': "width: 10em;"
        },
        'icon': {
            'style': "width: 15em;"
        },
        'points': {
            'style': "width: 5em;"
        }
    }
    edit_template = 'admin/editaward.html'
    create_template = 'admin/createaward.html'
    column_default_sort = ('timestamp', True)
    semester = models.Semester.query.filter_by(current=True).first()
    form_args = dict(points=dict(validators=[NumberRange(min=0)]),
                     semester=dict(default=semester),
                     brothers=dict(query_factory=
                        lambda: models.Brother.query.filter_by(active=True))
                     )

    def __init__(self, session):
        super(AwardModelView, self).__init__(models.Award, session)

    def get_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(self.model).filter(self.model.semester==semester)

    def get_count_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(func.count('*')).filter(self.model.semester==semester)

class ServiceModelView(ProtectedModelView):
    form_excluded_columns = ('email_sent')
    column_exclude_list = ('email_sent')
    column_default_sort = ('approved')
    form_args = dict(brother=dict(query_factory=
                        lambda: models.Brother.query.filter_by(active=True)),
                     weight=dict(default=1.0)
                     )

    def __init__(self, session):
        super(ServiceModelView, self).__init__(models.Service, session)

    def is_accessible(self):
        if current_user.is_authenticated and current_user.position and \
                ("service" in current_user.position.name.lower() or current_user.is_admin()):
            return True
        return False

    def on_model_change(self, form, model, is_created):
        if form.approved.data:
            semester = models.Semester.query.filter_by(current=True).one()
            donehrs = form.brother.data.total_service_hours(semester)
            svchrs = (form.end.data - form.start.data).seconds/3600.0
            remaining = semester.required_service - donehrs
            if not model.email_sent:
                svcmsg ="The service hours you reported for '{}' have just been approved by {} (The weight for this service was {}). ".format(
                    form.name.data,
                    current_user.name,
                    model.weight)
                if remaining > 0:
                    svcmsg += "You have {} service hour(s) left to do this semester (out of {}).".format(remaining, semester.required_service)
                else:
                    svcmsg += "You have completed your service hours for this semester! You currently have {}.".format(donehrs)
                send_email("Service Chair (points)",
                           str(svchrs*float(model.weight)) + " service hour" +
                           ("" if svchrs == 1 else "s") + " have been approved!",
                           [form.brother.data.email],
                           svcmsg,
                           svcmsg
                           )
                model.email_sent = True
                db.session.add(model)
                db.session.commit()
        else:
            model.email_sent = False
            db.session.add(model)
            db.session.commit()

    def on_model_delete(self, model):
        semester = models.Semester.query.filter_by(current=True).one()
        donehrs = model.brother.total_service_hours(semester)
        svchrs = (model.end - model.start).seconds/3600.0
        remaining = semester.required_hours - donehrs
        svcmsg ="The {} ({}*{}) service hour(s) you reported for '{}' have been denied by {}. If you want to know why you should ask them about it! ".format(
            svchrs*float(model.weight),
            svchrs,
            float(model.weight),
            model.name,
            current_user.name)
        if remaining > 0:
            svcmsg += "You have {} service hour(s) left to do this semester (out of {}).".format(remaining, semester.required_service)
        else:
            svcmsg += "You have completed your service hours for this semester! You currently have {}.".format(donehrs)
        send_email("Service Chair (points)",
                   "Service hours have been DENIED!",
                   [model.brother.email],
                   svcmsg,
                   svcmsg)

    def get_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(self.model).filter(self.model.semester==semester)

    def get_count_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(func.count('*')).filter(self.model.semester==semester)

class SignUpSheetsView(ProtectedModelView):
    create_template = 'admin/createsignup.html'
    edit_template = 'admin/editsignup.html'
    form_excluded_columns = ["roles"]
    form_args = dict(semester=dict(default=models.Semester.query.filter_by(current=True).one()),
                     event=dict(query_factory=
                        lambda: models.Event.query.filter_by(semester=models.Semester.query.filter_by(current=True).one())
                                )
                     )

    def __init__(self, session):
        super(ProtectedModelView, self).__init__(models.SignUpSheet, session)

    def get_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(self.model).filter(self.model.semester==semester)

    def get_count_query(self):
        semester = models.Semester.query.filter_by(current=True).one()
        return self.session.query(func.count('*')).filter(self.model.semester==semester)

    def on_model_change(self, form, model, is_created):
        #TODO: stop being a savage and put form data into a data structure
        nums = []
        names = []
        for key in request.form.keys():
            if "role-name" in key and key.split('-')[-1] not in nums:
                nums.append(key.split('-')[-1])
                names.append(request.form[key])
        #create all roles from scratch
        if is_created:
            for num in nums:
                self.add_or_edit_role(model, num)
        #edit roles
        else:
            #modify existing roles or add new ones
            for num in nums:
                roles = models.SignUpRole.query.filter_by(name=request.form['role-name-'+num], signupsheet=model).all()
                for role in roles:
                    self.add_or_edit_role(model, num, role)
                if len(roles) == 0:
                    self.add_or_edit_role(model, num)
            #if a name is not in the names array but is in the model.roles then delete the role
            for n in models.SignUpRole.query.filter_by(signupsheet=model).all():
                if n.name not in names:
                    #TODO: delete members in that role
                    db.session.delete(n)
        db.session.commit()

    def add_or_edit_role(self, model, num, role=None):
        if role:
            try: max = request.form['role-max-'+num]
            except: max = request.form['role-min-'+num]
            role.max = max
            role.min = request.form['role-min-'+num]
            role.name = request.form['role-name-'+num]
            db.session.add(role)
        else:
            try: max = request.form['role-max-'+num]
            except: max = request.form['role-min-'+num]
            role = models.SignUpRole(name=request.form['role-name-'+num], min=request.form['role-min-'+num], max=max, signupsheet=model)
            db.session.add(role)

    def on_model_delete(self, model):
        #TODO: delete users that are part of each role
        for r in model.roles:
            db.session.delete(r)
        db.session.commit()

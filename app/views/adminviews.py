from app import app, db, models
from flask.ext.admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask.ext.login import current_user
from flask import redirect, url_for, flash
from config import USER_ROLES

class IndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated() and current_user.role > 0:
            return True
        return False

    def _handle_view(self, name, **kwargs):
            if not self.is_accessible():
                flash("You don't have permission to go there", category="warning")
                return redirect(url_for('main.index'))

class ProtectedModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated() and current_user.role > 0:
            if current_user.role == 1:
                self.can_create = False
                self.can_delete = False
                self.can_edit = False
            return True
        return False

    def _handle_view(self, name, **kwargs):
            if not self.is_accessible():
                flash("You don't have permission to go there", category="warning")
                return redirect(url_for('main.index'))

class AdminModelView(ProtectedModelView):
    def is_visible(self):
        if current_user.is_authenticated() and current_user.role != 2:
            return False
        return True

class BrotherModelView(AdminModelView):
    column_exclude_list = ['points']
    column_default_sort = ('active', True)
    can_create = False
    column_display_pk = True
    column_hide_backrefs = False
    form_excluded_columns = ('points', 'awards', 'events')
    def __init__(self, session):
        super(BrotherModelView, self).__init__(models.Brother, session)

class FamilyModelView(AdminModelView):
    can_create = False
    can_edit = False
    def __init__(self, session):
        super(FamilyModelView, self).__init__(models.Family, session)

class EventModelView(ProtectedModelView):
    can_create = True
    can_delete = True
    can_edit = True
    form_excluded_columns = ('code')
    semester = models.Semester.query.filter_by(current=True).first()
    form_args = dict(semester=dict(default=semester))
    def __init__(self, session):
        super(EventModelView, self).__init__(models.Event, session)

class PointsModelView(ProtectedModelView):
    can_create = True
    can_delete = True
    can_edit = True
    semester = models.Semester.query.filter_by(current=True).first()
    form_args = dict(semester=dict(default=semester))
    def __init__(self, session):
        super(PointsModelView, self).__init__(models.OtherPoints, session)

class SemesterModelView(AdminModelView):
    column_default_sort = ('current', True)
    def __init__(self, session):
        super(SemesterModelView, self).__init__(models.Semester, session)

class AwardModelView(ProtectedModelView):
    can_create = True
    can_delete = True
    can_edit = True
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
    semester = models.Semester.query.filter_by(current=True).first()
    form_args = dict(semester=dict(default=semester))
    def __init__(self, session):
        super(AwardModelView, self).__init__(models.Award, session)

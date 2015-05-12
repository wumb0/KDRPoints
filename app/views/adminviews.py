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

class BrotherModelView(ProtectedModelView):
    column_exclude_list = ['points']
    can_create = False
    column_display_pk = True
    column_hide_backrefs = False
    form_excluded_columns = ('points', 'awards', 'events')
    def __init__(self, session):
        super(BrotherModelView, self).__init__(models.Brother, session)

class FamilyModelView(ProtectedModelView):
    can_create = False
    can_edit = False
    def __init__(self, session):
        super(FamilyModelView, self).__init__(models.Family, session)

class EventModelView(ProtectedModelView):
    def __init__(self, session):
        super(EventModelView, self).__init__(models.Event, session)

class PointsModelView(ProtectedModelView):
    def __init__(self, session):
        super(PointsModelView, self).__init__(models.OtherPoints, session)

class SemesterModelView(ProtectedModelView):
    def __init__(self, session):
        super(SemesterModelView, self).__init__(models.Semester, session)

class AwardModelView(ProtectedModelView):
    def __init__(self, session):
        super(AwardModelView, self).__init__(models.Award, session)

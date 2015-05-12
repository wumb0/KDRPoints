from app import app
from flask.ext.admin import AdminIndexView
from flask.ext.login import current_user
from flask import redirect, url_for, flash
from config import USER_ROLES

#class AuthMixin(object):
#    def _handle_view(self, name, **kwargs):
#        if not current_user.is_authenticated():
#            return app.login_manager.unauthorized()
#        if not current_user.is_admin():
#            abort(403)

class IndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated() and current_user.role > 0:
            return True
        return False

    def _handle_view(self, name, **kwargs):
            if not self.is_accessible():
                flash("You don't have permission to go there", category="warning")
                return redirect(url_for('main.index'))

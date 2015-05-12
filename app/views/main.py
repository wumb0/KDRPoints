#!flask/bin/python
from app import db, app, lm, google
from datetime import datetime
from flask import render_template, url_for, session, g, redirect, Blueprint, flash, abort
from flask.ext.login import logout_user, login_user, current_user, current_user, login_required
from app.models import *
from config import USER_ROLES
from app.forms import *

main = Blueprint('main', __name__)

@main.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
            redirect(url_for(".first_login"))

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html', title='Home')

@lm.user_loader
def load_user(id):
    return Brother.query.get(int(id))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@main.route('/login')
def login():
    if g.user.is_authenticated():
        flash("You are already logged in as {}.".format(g.user.email), category="warning")
        return redirect(url_for(".index"))
    session.pop('google_token', None)
    return google.authorize(callback=url_for('.authorized', _external=True))

@main.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('.index'))

@main.route('/login/authorized')
@google.authorized_handler
def authorized(response):
    if response is None:
        flash("Login failed", category='error')
        return redirect(url_for("main.index"))
    session['google_token'] = (response['access_token'], '')
    me = google.get('userinfo')

    if me.data['email'][-9:].lower() != "kdrib.org":
        me = None
        response = None
        logout_user()
        session.clear()
        flash("Log in with your @kdrib.org account!", category="warning")
        return redirect(url_for('main.index'))
    bro = Brother.query.filter_by(email=me.data['email']).first()
    if bro is None:
        bro = Brother(name=me.data['name'], nickname="", email=me.data['email'], position="None", pin=0)
        db.session.add(bro)
        db.session.commit()
    login_user(bro, remember = False)
    if bro.pin == 0 or bro.family is None:
        return redirect(url_for('main.first_login'))
    return redirect(url_for("main.index"))

def flash_wtferrors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("{} - {}".format(field, error), category="error")

@main.route('/login/first', methods = ['GET', 'POST'])
@login_required
def first_login():
    bro = g.user
    if bro.pin != 0 or bro.family != None:
        flash("This page is meant for initial registrants only, change profile information on the edit profile page", category="error")
        abort(404)
    flogin_form = FirstLoginForm()
    if flogin_form.validate_on_submit():
        bro.pin = flogin_form.pin.data
        bro.name = flogin_form.name.data
        bro.nickname = flogin_form.nickname.data
        bro.family_id = flogin_form.family.data
        db.session.add(bro)
        db.session.commit()
        flash("Registered sucessfully!", category="good")
        return redirect(url_for('main.index'))
    else:
        flash_wtferrors(flogin_form)
    flogin_form.name.default = bro.name
    flogin_form.process()
    return render_template('first_login.html', form=flogin_form)

@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html')

#!flask/bin/python
from app import db, app, lm, google
from datetime import datetime
from flask import render_template, url_for, session, g, redirect, Blueprint, flash, abort
from flask.ext.login import logout_user, login_user, current_user, current_user, login_required
from app.models import *
from config import USER_ROLES
from app.forms import *
from sqlalchemy import desc

main = Blueprint('main', __name__)

@main.before_request
def before_request():
    g.user = current_user
    g.current_semester = Semester.query.filter_by(current=True).first()

@main.route('/')
@main.route('/index')
def index():
    if g.user.is_authenticated():
        name=g.user.name.split(" ")[0]
    else:
        name = "stranger"
    return render_template('index.html', title='Home', name=name)

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
@login_required
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
    return render_template('first_login.html', title="First Login", form=flogin_form)

@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html')

@main.route('/attend', methods = ["GET", "POST"])
def attend():
    form = AttendForm()
    #remove this
    current_semester = Semester.query.filter_by(current=True).first()
    events_query = Event.query.filter_by(event_picker=True, semester_id=current_semester.id).all()
    events = []
    if events is not None:
        events = [ (x.id, x.name) for x in events_query ]
    form.event.choices = events
    if form.validate_on_submit():
        bro = Brother.query.filter_by(pin=form.pin.data).first()
        if bro is not None:
            event = Event.query.filter_by(id=form.event.data).first()
            if not event.code_enable or form.code.data == event.code:
                if bro not in event.brothers:
                    event.brothers.append(bro)
                    db.session.commit()
                    flash("Signed in to the event", category="good")
                else:
                    flash("You have already signed in", category="warning")
            else:
                flash("The event code was not correct", category="error")
    else:
        flash_wtferrors(form)
    return render_template('attend.html', title="Attend", form=form, events=events_query)

@main.route('/profile')
@login_required
def profile():
    all_brothers = Brother.query.filter_by(active=True)
    avg = sum([ x.get_all_points(g.current_semester) for x in all_brothers ]) / all_brothers.count()
    all_items = g.user.events.filter_by(semester=g.current_semester).all() + g.user.awards.filter_by(semester=g.current_semester).all()+ g.user.points.filter_by(semester=g.current_semester).all()
    all_items.sort(key=lambda x: x.timestamp, reverse=True)
    return render_template("profile.html", title="Profile", avg=avg, all_items=all_items[:10], Event=Event, Award=Award, OtherPoints=OtherPoints, isinstance=isinstance)

@main.route('/founderscup')
@login_required
def founderscup():
    families = sorted(Family.query.all(), key=lambda x: x.get_points(g.current_semester), reverse=True)
    return render_template("founders_cup.html", title="Founders Cup", families=families)

@main.route('/edit_nickname', methods = ['GET', 'POST'])
@login_required
def edit_nickname():
    form = EditNickForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        db.session.add(g.user)
        db.session.commit()
        return redirect(url_for('.profile'))
    return render_template("edit_nickname.html", title="Edit Nickname", form=form)

@main.route('/awards')
@login_required
def awards():
    all_items = Award.query.filter_by(semester=g.current_semester).order_by(desc(Award.timestamp))
    return render_template('awards.html', title="Awards", all_items=all_items, isinstance=isinstance, Event=Event, Award=Award, OtherPoints=OtherPoints)

@main.route('/events')
@login_required
def events():
    all_items = Event.query.filter_by(semester=g.current_semester).order_by(desc(Event.timestamp))
    return render_template('events.html', title="Events", all_items=all_items, isinstance=isinstance, Event=Event, Award=Award, OtherPoints=OtherPoints)

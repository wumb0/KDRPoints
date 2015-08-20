#!flask/bin/python
from app import db, app, lm, google
from datetime import datetime
from flask import render_template, url_for, session, g, redirect, Blueprint, flash, abort, request
from flask.ext.login import logout_user, login_user, current_user, current_user, login_required
from app.models import *
from config import USER_ROLES
from app.forms import *
from app.email import send_email
from sqlalchemy import desc
from urlparse import urlparse

main = Blueprint('main', __name__)

@main.before_request
def before_request():
    g.user = current_user
    g.current_semester = Semester.query.filter_by(current=True).first()
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

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
        bro = Brother(name=me.data['name'], nickname="", email=me.data['email'], position=None, pin=0)
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
    form = FirstLoginForm()
    if form.validate_on_submit():
        bro.pin = form.pin.data
        bro.name = form.name.data
        bro.nickname = form.nickname.data
        bro.family_id = form.family.data
        bro.active = form.active.data
        db.session.add(bro)
        db.session.commit()
        flash("Registered sucessfully!", category="good")
        return redirect(url_for('main.index'))
    else:
        flash_wtferrors(form)
    form.name.default = bro.name
    form.process()
    return render_template('first_login.html', title="First Login", form=form)

@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html')

@main.route('/attend', methods = ["GET", "POST"])
def attend():
    form = AttendForm()
    events_query = Event.query.filter_by(event_picker=True, semester=g.current_semester).all()
    events = []
    if events is not None:
        events = [ (x.id, x.name) for x in events_query ]
    if g.user.is_authenticated():
        form.pin.data = g.user.pin
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

@main.route('/profile', methods = [ 'GET', 'POST' ])
@login_required
def profile():
    form = EditNickForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        db.session.add(g.user)
        db.session.commit()
        return redirect(url_for('.profile'))
    else:
        flash_wtferrors(form)
    avgpoints, avgsvc = __get_avg_points()
    all_items = g.user.events.filter_by(semester=g.current_semester).all() + g.user.awards.filter_by(semester=g.current_semester).all()+ g.user.points.filter_by(semester=g.current_semester).all()
    all_items.sort(key=lambda x: x.timestamp, reverse=True)
    return render_template("profile.html", title="Profile", avgpoints=avgpoints, avgsvc=avgsvc, all_items=all_items[:10], Event=Event, Award=Award, OtherPoints=OtherPoints, isinstance=isinstance, form=form)

@main.route('/allbrotherpoints/<username>')
@login_required
def allbrotherpoints(username):
    user = Brother.query.filter_by(email=username + "@kdrib.org").first()
    if not user or not g.user.is_admin():
        abort(404)
    all_items = (user.events.all() +
                 user.awards.all() +
                 user.points.all())
    all_items.sort(key=lambda x: x.timestamp, reverse=True)
    return render_template("allpoints.html",
                           title="All Points - {}".format(user.name),
                           all_items=all_items,
                           Event=Event,
                           Award=Award,
                           OtherPoints=OtherPoints,
                           isinstance=isinstance,
                           user=user)

@main.route('/allpoints')
@login_required
def allpoints():
    all_items = (g.user.events.all() +
                 g.user.awards.all() +
                 g.user.points.all())
    all_items.sort(key=lambda x: x.timestamp, reverse=True)
    return render_template("allpoints.html",
                           title="All Points",
                           all_items=all_items,
                           Event=Event, Award=Award,
                           OtherPoints=OtherPoints,
                           isinstance=isinstance,
                           user=g.user)

@main.route('/founderscup')
@login_required
def founderscup():
    families = sorted(Family.query.all(), key=lambda x: x.get_points(g.current_semester), reverse=True)
    return render_template("founders_cup.html", title="Founders Cup", families=families)

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

@main.route('/brothers')
@login_required
def brothers():
    brothers = Brother.query.filter_by(active=True).order_by(Brother.pin).all()
    avgpoints, avgsvc = __get_avg_points()
    return render_template("brothers.html", title="Brothers", brothers=brothers, avg=avgpoints)

@main.route('/allbrothers')
@login_required
def all_brothers():
    brothers = sorted(Brother.query.all(), key=lambda x: x.pin)
    return render_template("brothers.html", title="All Brothers", brothers=brothers, avg=0)

@main.route('/event/<id>')
@login_required
def event(id):
    event = Event.query.filter_by(id=id).first()
    if event is None:
        abort(404)
    return render_template('event.html', title=event.name, event=event)

@main.route('/award/<id>')
@login_required
def award(id):
    award = Award.query.filter_by(id=id).first()
    if award is None:
        abort(404)
    return render_template('award.html', title=award.name, award=award)

@main.route('/service', methods = ['GET', 'POST'])
@login_required
def service():
    form = ServiceForm()
    if form.validate_on_submit():
        serv = Service(brother_id=g.user.id,
                       start=form.start.data,
                       end=form.end.data,
                       info=form.info.data,
                       name=form.name.data,
                       semester_id=g.current_semester.id)
        db.session.add(serv)
        db.session.commit()
        try:
            svcid = Position.query.filter_by(name="Service Chair").first()
            svcchair = Brother.query.filter_by(position_id=svcid.id).first()
            path = urlparse(request.base_url)
            body = "{} has submitted service hours for approval. Go to {}://{}{}?id={} to review.".format(
                    g.user.name, path.scheme, path.netloc, url_for('service.edit_view'), serv.id)
            send_email("KDRPoints",
                    "Service hours submitted by " + g.user.name,
                        [svcchair.email],
                        body,
                        body)
        except: pass

        flash("Service submitted successfully", category="good")
    else:
        flash_wtferrors(form)
    return render_template('service.html', title="Service", form=form)

@main.route('/allservice')
@login_required
def allservice():
    return redirect(url_for('.allservicesemester',
                            semester=g.current_semester.linkname))

@main.route('/allservice/<semester>')
@login_required
def allservicesemester(semester):
    semesterobj = Semester.query.filter_by(linkname=semester).first()
    if g.user.is_normal_user() or not semesterobj:
        abort(404)
    brothers = Brother.query.filter_by(active=True)
    return render_template('allservice.html',
                           title="all service",
                           brothers=brothers,
                           semester=semesterobj)



def __get_avg_points():
    all_brothers = Brother.query.filter_by(active=True)
    if all_brothers.count() > 0:
        avgpoints = sum([ x.get_all_points(g.current_semester) for x in all_brothers ]) / all_brothers.count()
        avgsvc = sum([ x.total_service_hours(g.current_semester) for x in all_brothers ]) / all_brothers.count()
        avgpoints = round(avgpoints, 2)
        avgsvc = round(avgsvc, 2)
    else:
        avgpoints = 0
        avgsvc = 0
    return avgpoints, avgsvc

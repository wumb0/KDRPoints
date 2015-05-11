#!flask/bin/python
from app import db, app, lm, google
from datetime import datetime
from flask import render_template, url_for, session, g, redirect, Blueprint, flash
from flask.ext.login import logout_user, login_user, current_user, current_user
from app.models import *
from config import USER_ROLES
from app.forms import *

main = Blueprint('main', __name__)

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
    session.pop('google_token', None)
    return google.authorize(callback=url_for('.authorized', _external=True))

@main.route('/login/authorized')
def authorized(response):
    if response is None:
        flash("Login failed", category='error')
        return redirect(url_for(".index"))

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

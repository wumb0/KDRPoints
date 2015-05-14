#!flask/bin/python
from flask import Flask, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_oauthlib.client import OAuth
from flask_admin.contrib.sqla import ModelView
from config import GOOGLE_CONSUMER_KEY, GOOGLE_CONSUMER_SECRET
from flask.ext.admin import Admin
from flask_admin.base import MenuLink

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key= GOOGLE_CONSUMER_KEY,
    consumer_secret= GOOGLE_CONSUMER_SECRET,
    request_token_params={
        'scope' : 'https://www.googleapis.com/auth/userinfo.email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url = None,
    access_token_method = 'POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'main.login'

from app import models
db.create_all()
db.session.commit()
from app.views import main, adminviews

admin = Admin(app, 'KDR Points Admin', template_mode='bootstrap3', index_view=adminviews.IndexView())
admin.add_link(MenuLink(name='Back to Site', url='/'))
admin.add_view(adminviews.EventModelView(db.session))
admin.add_view(adminviews.AwardModelView(db.session))
admin.add_view(adminviews.PointsModelView(db.session))
admin.add_view(adminviews.BrotherModelView(db.session))
admin.add_view(adminviews.FamilyModelView(db.session))
admin.add_view(adminviews.SemesterModelView(db.session))
app.register_blueprint(main.main)

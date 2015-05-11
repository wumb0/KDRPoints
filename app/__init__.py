from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_oauthlib.client import OAuth
from config import GOOGLE_CONSUMER_KEY, GOOGLE_CONSUMER_SECRET

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
lm.login_view = 'login'

from app import models
from app.views import main

app.register_blueprint(main.main)

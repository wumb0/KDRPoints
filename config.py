import os

basedir = os.path.abspath(os.path.dirname(__file__))
f = open(os.path.join(basedir, 'app.vars') , 'r')

#SERVER_NAME = 'points.kdrib.org'
CSRF_ENABLED = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repo')
SECRET_KEY = f.readline().strip()
GOOGLE_CONSUMER_KEY = f.readline().strip()
GOOGLE_CONSUMER_SECRET = f.readline().strip()
BASE_ADMINS = [ x.rstrip() for x in f.readline().split(',') ]
USER_ROLES = {'admin':2,'chair':1,'user':0}

f.close()

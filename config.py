import os

basedir = os.path.abspath(os.path.dirname(__file__))
f = open(os.path.join(basedir, 'app.vars') , 'r')

#SERVER_NAME = 'points.kdrib.org'
CSRF_ENABLED = True

MYSQL_DB = f.readline().strip()
MYSQL_HOST = f.readline().strip()
MYSQL_USERNAME = f.readline().strip()
MYSQL_PASSWORD = f.readline().strip()
SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_USERNAME + ":" + MYSQL_PASSWORD + "@" + MYSQL_HOST + ":3306/" + MYSQL_DB
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repo')
SECRET_KEY = f.readline().strip()
GOOGLE_CONSUMER_KEY = f.readline().strip()
GOOGLE_CONSUMER_SECRET = f.readline().strip()
USER_ROLES = {'admin':2,'chair':1,'user':0}
f.close()

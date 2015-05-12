#!/var/www/finishyour.beer/flask/bin/python

from flup.server.fcgi import WSGIServer
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/finishyour.beer/")

from app import app
from app import app as application

if __name__ == '__main__':
	WSGIServer(app).run()

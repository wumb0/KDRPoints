from flask.ext.mail import Message
from app import app, mail
from config import MAIL_USERNAME
from threading import Thread

def async(f):
    '''spawns a new thread when the decorated function is called
    arg:
        f - the function to thread
    '''
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper

@async
def send_async_email(msg):
    '''send an email in another thread, see decorators.py
    arg:
        msg - the Message object to send
    '''
    with app.app_context():
        mail.connect()
        mail.send(msg)

def send_email(sender, subject, recipients, text_body, html_body):
    '''setup the email to be sent
    args:
        subject - the subject of the email to be sent
        recipients - the recipients of the email to be sent
        text_body - the body of the email to be sent, in plain text
        html_body - the body of the email to be sent, in html
    '''
    sender = (sender, MAIL_USERNAME)
    msg = Message(subject, sender = sender, bcc = recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(msg)

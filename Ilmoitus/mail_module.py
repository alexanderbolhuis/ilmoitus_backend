from webob.acceptparse import NoAccept
from webob.dec import _MiddlewareFactory

__author__ = 'Sjors_Boom'

from google.appengine.api import mail
from error_response_module import give_error_response


def send_email_to_user(request_handler, sender, to, subject, body, html_body=None):
    if not mail.is_email_valid(sender):
        give_error_response(request_handler, 500, "sender is not a valid E-mail address: \"" + sender + "\"")

    if not mail.is_email_valid(to):
        give_error_response(request_handler, 500, "to is not a valid E-mail address: \"" + to + "\"")

    if body is not None:
        give_error_response(request_handler, 500, "body is None")
    message = mail.EmailMessage()
    message.sender = sender
    message.to = to
    message.subject = subject
    message.body = body
    if html_body is not None:
        message.html = html_body

    message.send()


def create_begin_of_the_body(name):
    return "Dear " + name + ", \n\n"

def create_ending_of_the_body():
    return "With kind regards,\n\nIlmoitus team"

def create_body(name, middle_body):
    return create_begin_of_the_body(name) + middle_body + create_ending_of_the_body()
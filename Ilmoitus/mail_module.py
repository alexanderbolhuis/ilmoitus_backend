from webob.acceptparse import NoAccept

__author__ = 'Sjors_Boom'

from google.appengine.api import mail
import ilmoitus_model

default_sender = "info.sns-ilmoitus@gmail.com"  # TODO: Check


def send_email_to_user(request_handler, sender, to, subject, body, html_body=None):
    if not mail.is_email_valid(sender):
        request_handler.give_error_response(500, "sender is not a valid E-mail address: \"" + sender + "\"")

    if not mail.is_email_valid(to):
        request_handler.give_error_response(500, "to is not a valid E-mail address: \"" + to + "\"")

    if body is None:
        request_handler.give_error_response(500, "body is None")
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


def send_mail_declaration_approved(request_handler, declaration):
    person_to = ilmoitus_model.Person.get_by_id(declaration.created_by.integer_id())

    body = create_begin_of_the_body(person_to.last_name) + \
           "We send this email because your submitted declaration (submitted on " + \
           declaration.created_at.strftime('%Y-%m-%d %H:%M') + " is completely approved and it will be payed out on: "+\
           str(declaration.will_be_payed_out_on)

    send_email_to_user(request_handler, default_sender, person_to.email, "Your declaration is approved", body)
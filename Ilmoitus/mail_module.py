from webob.acceptparse import NoAccept
from webob.dec import _MiddlewareFactory

__author__ = 'Sjors_Boom'

from google.appengine.api import mail
from ilmoitus_model import *
from error_response_module import give_error_response

default_sender = "developers.42IN11EWa@gmail.com"  # TODO: Check


def send_email_to_user(request_handler, sender, to, subject, body, html_body=None):
    if not mail.is_email_valid(sender):
        give_error_response(request_handler, 500, "sender is not a valid E-mail address: \"" + sender + "\"")

    if not mail.is_email_valid(to):
        give_error_response(request_handler, 500, "to is not a valid E-mail address: \"" + to + "\"")

    if body is None:
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
    return "\n\nWith kind regards,\n\nIlmoitus team"


def send_mail_new_declaration_submitted(request_handler, declaration):
    person = Person.get_by_id(declaration.assigned_to[len(declaration.assigned_to)-1].integer_id())
    to = person.email
    body = create_body(person.last_name,
                       "We send you this email to inform you that a new declaration has just been submitted and " +
                       "is awaiting your approval.")

    send_email_to_user(request_handler, default_sender, to, "A new declaration awaits your approval.", body)


def send_message_declaration_status_changed(request_handler, declaration):
    person = Person.get_by_id(declaration.created_by.integer_id())
    to = person.email
    body = create_body(person.last_name,
                       "We send you this email to inform you that the status of your declaration (submitted on " +
                       declaration.created_at.strftime('%Y-%m-%d %H:%M') +
                       "). Has changed to \"" + declaration.readable_state() + "\".")

    send_email_to_user(request_handler, default_sender, to, "The status or your declaration has changed.", body)


def send_mail_declaration_approved(request_handler, declaration):
    person_to = Person.get_by_id(declaration.created_by.integer_id())

    body = create_body(person_to.last_name, "We send this email because your submitted declaration (submitted on " +
           declaration.created_at.strftime('%Y-%m-%d %H:%M') + " is completely approved and it will be payed out on: " +
           str(declaration.will_be_payed_out_on))

    send_email_to_user(request_handler, default_sender, person_to.email, "Your declaration is approved", body)


def create_body(name, middle_body):
    return create_begin_of_the_body(name) + middle_body + create_ending_of_the_body()

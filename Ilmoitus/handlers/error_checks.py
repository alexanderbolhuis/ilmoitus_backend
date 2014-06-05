__author__ = 'Robin'
from ilmoitus_auth import *


def find_declaration(handler, declaration_id):
    safe_id = convert_to_long(handler, declaration_id)
    declaration = Declaration.get_by_id(safe_id)
    if declaration is None:
        give_error_response(handler, 404, "Declaratie ["+str(safe_id)+"] niet gevonden",
                                          "Declaration is None")

    return declaration


def find_employee(handler, employee_id):
    safe_id = convert_to_long(handler, employee_id)
    employee = Person.get_by_id(safe_id)
    if employee is None:
        give_error_response(handler, 404, "Werknemer ["+str(safe_id)+"] niet gevonden",
                                          "Person is None")

    return employee


def find_attachment(handler, attachment_id):
    safe_id = convert_to_long(handler, attachment_id)
    attachment = Attachment.get_by_id(safe_id)
    if attachment is None:
        give_error_response(handler, 404, "Attachment ["+str(safe_id)+"] niet gevonden",
                                          "Attachment is None")

    return attachment


def find_declaration_type(handler, declaration_type_id):
    safe_id = convert_to_long(handler, declaration_type_id)
    declaration = DeclarationType.get_by_id(safe_id)
    if declaration is None:
        give_error_response(handler, 404, "Declaratie type ["+str(safe_id)+"] niet gevonden",
                                          "Declaration type is None")

    if len(declaration.sub_types) == 0:
        give_error_response(handler, 404, "Declaratie type ["+str(safe_id)+"] is leeg",
                                          "Declaration type has no children")

    return declaration


def is_declaration_creator(handler, declaration, employee):
    if declaration.created_by.key.integer_id() != employee.key.integer_id():
        give_error_response(handler, 401, "Declaratie kan niet worden aangepast.",
                                          "User is not the owner")


def is_declaration_assigned(handler, declaration, current_person):
    if current_person.key != declaration.get_last_assigned_to():
        give_error_response(handler, 401, "Kan de declaratie niet goedkeuren. Deze declaratie is niet aan u toegewezen",
                                          "current_person_object's id was not in the declaration_object's asigned_to list")


def is_declaration_price_allowed_supervisor(handler, declaration, current_person):
    if current_person.max_declaration_price < declaration.items_total_price and current_person.max_declaration_price != -1:
        give_error_response(handler, 400, "De huidige persoon mag deze declaratie niet goedkeuren. Bedrag te hoog",
                            "Total item costs is: " + str(declaration.items_total_price) + " and the max amount is: "
                            + str(current_person.max_declaration_price))


def is_declaration_state(handler, declaration, class_name):
    if declaration.class_name != class_name:
        give_error_response(handler, 400, "Declaratie heeft niet de jusite status voor deze actie",
                                          "Expected state: " + class_name + " Received state: " + declaration.class_name)


def has_post(handler, post, readable_post, break_if_missing=False, stringify=True):
    if handler.request.body is not None:
        request_body = json.loads(handler.request.body)
        if post in request_body.keys() and request_body[post] is not None and request_body[post] != "":
            if stringify:
                return str(request_body[post])
            else:
                return request_body[post]
    if break_if_missing:
        give_error_response(handler, 400, "Geen " + readable_post + " ontvangen.", post + " is None")


def is_current_person_supervisor(handler, current_person):
    if current_person.class_name != "supervisor":
        give_error_response(handler, 401, "Kan de declaratie niet doorsturen. Deze persoon is geen leidinggevende",
                            "current_person_object's id is not an supervisor")


def is_declaration_states(handler, declaration, class_names):
    found = False
    for class_name in class_names:
        found |= declaration.class_name == class_name

    if not found:
        give_error_response(handler, 400, "Declaratie heeft niet de jusite status voor deze actie.",
                                          "Expected state: " + str(class_names) + " Received state: " + declaration.class_name)


def is_allowed_declaration_viewer(handler, declaration, current_user):
    if declaration.created_by != current_user.key and \
       (current_user.class_name != 'supervisor' or current_user.key not in declaration.assigned_to) and \
       current_user.class_name != 'human_resources':

        give_error_response(handler, 401, "U heeft niet de juiste rechten om deze declaratie te openen")


def if_employee_is_supervisor(handler, current_person):
    if current_person.class_name != "supervisor":
        give_error_response(handler, 401, "Kan de declaratie niet doorsturen. Deze persoon is geen leidinggevende",
                                          "current_person_object's id is not an supervisor")


def convert_to_long(handler, string):
    safe_id = 0
    try:
        safe_id = long(string)
    except ValueError:
        give_error_response(handler, 400, "Id is geen correcte waarde (" + str(string) + ")")

    return safe_id


def convert_to_float(handler, string):
    safe_id = 0
    try:
        safe_id = float(string)
    except ValueError:
        give_error_response(handler, 400, "Bedrag heeft geen correcte waarde (" + str(string) + ")")

    return safe_id


def find_declaration_sub_type(handler, sub_id):
    safe_id = convert_to_long(handler, sub_id)
    sub_type = DeclarationSubType.get_by_id(safe_id)
    if sub_type is None:
        give_error_response(handler, 404, "sub type ["+str(safe_id)+"] niet gevonden", "sub_type is None")
    return sub_type


def is_complete_dict(handler, dictcoll, elements, list_name):
    for key in elements:
        if key not in dictcoll.keys() or dictcoll[key] is None or dictcoll[key] == "":
            give_error_response(handler, 400, "Key "+key+" niet gevonden in " + list_name,
                                              "Key "+key+" not found")


def is_valid_declaration_attachment(handler, attachment):
    data = attachment["file"].split(":")[0]
    mime = attachment["file"].split(":")[1].split(";")[0]
    base = attachment["file"].split(":")[1].split(";")[1].split(",")[0]

    if data != "data" or base != "base64":
        give_error_response(handler, 400, "Kan geen declaratie toevoegen. De opgestuurde bijlage gegevens kloppen niet.",
                                          "The base64 string is incorrect.")

    if mime != "application/pdf" and mime.split("/")[0] != "image":
        give_error_response(handler, 400, "Kan geen declaratie toevoegen. Alleen pdf's of images zijn toegestaan.",
                                          "MimeType does not equal application/pdf or image/*", more_info=mime)
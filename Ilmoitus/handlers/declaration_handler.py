__author__ = 'RobinB'

from ilmoitus_auth import *
from response_module import *
from mail_module import *
import datetime
import mail_module
import dateutil.parser
import base64


def find_declaration(handler, declaration_id):
    safe_id = 0
    try:
        safe_id = long(declaration_id)
    except ValueError:
        give_error_response(handler, 400, "Id is geen correcte waarde (" + str(declaration_id) + ")")

    declaration = Declaration.get_by_id(safe_id)
    if declaration is None:
        give_error_response(handler, 400, "Declaratie ["+str(safe_id)+"] niet gevonden",
                                          "Declaration is None")

    return declaration

def is_declaration_creator(handler, declaration, employee):
    if declaration.created_by is not employee:
        give_error_response(handler, 401, "Declaratie kan niet worden aangepast.",
                                          "User is not the owner")


def is_declaration_assigned(handler, declaration, current_person):
    if current_person.key is not declaration.get_last_assigned_to():
        give_error_response(handler, 401, "Kan de declaratie niet goedkeuren. Deze declaratie is niet aan u toegewezen",
                                          "current_person_object's id was not in the declaration_object's asigned_to list")


def is_declaration_price_allowed_supervisor(handler, declaration, current_person):
    if current_person.max_declaration_price < declaration.items_total_price and current_person.max_declaration_price != -1:
        give_error_response(handler, 401, "De huidige persoon mag deze declaratie niet goedkeuren. Bedrag te hoog",
                            "Total item costs is: " + str(current_person.items_total_price) + " and the max amount is: "
                            + str(current_person.max_declaration_price))


def is_declaration_state(handler, declaration, class_name):
    if declaration.class_name != class_name:
        give_error_response(handler, 400, "Declaratie heeft niet de jusite status voor deze actie",
                                          "Expected state: " + class_name + " Received state: " + declaration.class_name)


def has_post(handler, post):
    if handler.request.POST[post] is None:
        give_error_response(handler, 400, "Geen " + has_post + " ontvangen", has_post + " is None")


def is_declaration_states(handler, declaration, class_names):
    found = False
    for class_name in class_names:
        found |= declaration.class_name == class_name

    if not found:
        give_error_response(handler, 400, "Declaratie heeft niet de jusite status voor deze actie.",
                                          "Expected state: " + str(class_names) + " Received state: " + declaration.class_name)


class OpenToLockedDeclarationHandler(BaseRequestHandler):
    def put(self, declaration_id):
        #Checks (break when fails)
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)
        is_declaration_creator(self, declaration, self.logged_in_person())
        is_declaration_state(self, declaration, "open_declaration")

        #Action
        declaration.locked_at = datetime.datetime.now()
        declaration.put()
        response_module.give_response(self, declaration.get_object_json_data())


class ForwardDeclarationHandler(BaseRequestHandler):
    def put(self, declaration_id):
        #Checks (break when fails)
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)


class DeclineBySupervisorHandler(BaseRequestHandler):
    def put(self, declaration_id):
        #Checks (break when fails)
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)
        is_declaration_states(self, declaration, {"locked_declaration", "open_declaration"})

        current_person = self.logged_in_person()

        #Checks (break when fails)
        has_post(self, "comment")
        is_declaration_assigned(self, declaration, current_person)
        is_declaration_price_allowed_supervisor(self, declaration, current_person)

        #Action
        declaration.class_name = "supervisor_declined_declaration"
        declaration.submitted_to_human_resources_by = current_person.key
        declaration.supervisor_approved_at = datetime.datetime.now()
        declaration.supervisor_comment = str(self.request.POST["comment"])
        declaration.put()

        send_message_declaration_status_changed(self, declaration)
        give_response(self, json.dumps(declaration.get_object_as_data_dict()))


class ApproveBySupervisorHandler(BaseRequestHandler):
    def put(self, declaration_id):
        #Checks (break when fails)
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)
        is_declaration_states(self, declaration, {"locked_declaration", "open_declaration"})

        current_person = self.logged_in_person()

        #Checks (break when fails)
        is_declaration_assigned(self, declaration, current_person)
        is_declaration_price_allowed_supervisor(self, declaration, current_person)

        #Action
        declaration.class_name = "supervisor_approved_declaration"
        declaration.submitted_to_human_resources_by = current_person.key
        declaration.supervisor_approved_at = datetime.datetime.now()

        if self.request.POST["comment"] is not None:
            declaration.supervisor_comment = str(self.request.POST["comment"])

        declaration.put()
        mail_module.send_message_declaration_status_changed(self, declaration)
        give_response(self, json.dumps(declaration.get_object_as_data_dict()))


class DeclineByHumanResourcesHandler(BaseRequestHandler):
    def put(self, declaration_id):
        person_data = ilmoitus_auth.get_current_person(self)
        person = person_data["person_value"]
        if person is not None:
            if person.class_name == "human_resources":  # person.key.class_name == "human_resources":
                if self.request.body is not None:
                    data = None
                    try:
                        data = json.loads(self.request.body)
                    except ValueError:

                        give_error_response(self, 500, "Kan de declaratie niet afkeuren omdat er ongeldige data "
                                                       "is verstuurd",
                                            "Invalid json data; Invalid format", more_info=str(self.request.body))
                    declaration_id = data['declaration_id']
                    person_key = person.key
                    current_date = datetime.datetime.now()
                    declaration = ilmoitus_model.Declaration.get_by_id(declaration_id)
                    if declaration.class_name == 'supervisor_approved_declaration':
                        declaration.class_name = 'human_resources_declined_declaration'
                        declaration.human_resources_declined_by = person_key
                        declaration.human_resources_declined_at = current_date
                        declaration.put()
                        mail_module.send_message_declaration_status_changed(self, declaration)
                        response_module.give_response(self, declaration.get_object_json_data())
                    else:
                        #
                        give_error_response(self, 500, "Kan de declaratie niet afkeuren omdat deze niet eerst "
                                                       "door een leidinggevende is goedgekeurd.",
                                            "Can only decline a supervisor_approved_declaration.")
                else:
                    #
                    give_error_response(self, 500, "Kan de declaratie niet afkeuren omdat er is geen data is "
                                                   "opgegeven.",
                                        "Request body is None!.")
            else:
                give_error_response(self, 401, "Kan de declaratie niet afkeuren omdat u niet de juiste "
                                               "permissie heeft.",
                                    "current_user is not from human_resources")
        else:
            give_error_response(self, 401, "Kan de declaratie niet afkeuren omdat u niet ingelogd bent.",
                                "current_user is None")


class ApproveByHumanResourcesHandler(BaseRequestHandler):
    def put(self, declaration_id):
        person_data = ilmoitus_auth.get_current_person(self)
        current_user = person_data["person_value"]

        if current_user is not None:
            if self.request.body is not None:
                data = None
                try:
                    data = json.loads(self.request.body)
                except ValueError:
                    give_error_response(self, 500, "Kan de declaratie niet goedkeuren omdat er ongeldige data "
                                                   "is verstuurd.",
                                        "Invalid JSON data; invalid format.", more_info=str(self.request.body))

                declaration_id = data["id"]
                pay_date = dateutil.parser.parse(data["pay_date"])
                today_date = datetime.datetime.now()

                declaration = ilmoitus_model.Declaration.get_by_id(declaration_id)

                if declaration.class_name == "supervisor_approved_declaration":
                    declaration.class_name = "human_resources_approved_declaration"
                    declaration.human_resources_approved_at = today_date
                    declaration.will_be_payed_out_on = pay_date
                    declaration.human_resources_approved_by = current_user.key
                    declaration.put()
                    mail_module.send_mail_declaration_approved(self, declaration)
                    response_module.give_response(self, declaration.get_object_json_data())
                else:
                    give_error_response(self, 500, "Kan de declaratie niet goedkeuren omdat deze niet eerst "
                                                   "door een leidinggevende is goedgekeurd.",
                                        "Can only approve a supervisor_approved_declaration.")
            else:
                give_error_response(self, 500, "Kan de declaratie niet goedkeuren omdat er is geen data is opgegeven.",
                                    "Request body is None.")
        else:
            #user does not have the appropriate permissions or isn't logged in at all.
            give_error_response(self, 401, "Geen permissie om een declaratie goed te keuren!",
                                "current_user is None or not from human_resources")


class NewDeclarationHandler(BaseRequestHandler):
    def post(self):
        # Check if logged in
        current_person_data = ilmoitus_auth.get_current_person(self)
        created_by = current_person_data["person_value"]

        if "user_is_logged_in" not in current_person_data.keys() or \
                not current_person_data["user_is_logged_in"]:
            give_error_response(self, 401,
                                "Er is niemand ingelogd.",
                                "get_current_person returned a False value for user_is_logged_in")
        # Check if body is set
        post_data = None
        try:
            post_data = json.loads(self.request.body)
        except ValueError:
            if self.request.body is None or len(self.request.body) <= 0:
                give_error_response(self, 400, "Er is geen declaratie opgegeven om aan te maken.",
                                    "Request body was None.")

        if post_data is None:
            give_error_response(self, 400, "Er is geen declaratie opgegeven om aan te maken.",
                                "Request.body did not contain valid json data")

        # Check if body contains declaration data
        declaration_data = None
        try:
            declaration_data = post_data["declaration"]
        except ValueError:
            give_error_response(self, 400, "Er is geen declaratie opgegeven om aan te maken.",
                                    "Request body was None.")

        # Check if body contains declarationlines
        declarationlines_data = None
        try:
            declarationlines_data = declaration_data["lines"]
        except ValueError:
            give_error_response(self, 400, "Er zijn geen declaratieitems opgegeven om aan te maken.",
                                    "Request body was None.")

        # Check if declaration has owner and assigned to values (mandatory)
        try:
            assigned_to = declaration_data["supervisor"]
        except Exception:
            give_error_response(self, 400, "De opgegeven data mist waardes voor een declaratie.",
                                "The body misses keys.")


        # Check if assigned_to is a valid user
        try:
            assigned_to = Person.get_by_id(int(assigned_to))
        except Exception:
            give_error_response(self, 400, "De supervisor is niet bekent in het systeem.",
                                "The supervisor is unknown.")

        # Check if assigned_to is a supervisor
        if assigned_to.class_name != "supervisor":
            give_error_response(self, 400, "De supervisor is niet bekent in het systeem.",
                                "The supervisor is unknown.")

        # Check if each declarationline has a receipt_date, a cost, and a declaration_sub_type
        try:
            for line in declarationlines_data:
                line["receipt_date"]
                line["cost"]
                line["declaration_sub_type"]
        except Exception:
            give_error_response(self, 400, "De opgegeven data mist waardes voor een declaratieline.",
                                "The body misses keys.")

        # Check if declaration subtypes exist
        for line in declarationlines_data:
            sub_type = ilmoitus_model.DeclarationSubType.get_by_id(int(line["declaration_sub_type"]))
            if sub_type is None:
                give_error_response(self, 400, "De declaratie_sub_type bestaat niet.",
                                    "The declaration_sub_type is unknown.")

        if "attachments" in declaration_data:
            try:
                for attachment_data in declaration_data["attachments"]:
                    attachment_data["name"]
                    attachment_data["file"]
            except KeyError:
                give_error_response(self, 400, "Kan geen declaratie toevoegen. De opgestuurde bijlage gegevens "
                                               "kloppen niet.",
                                    "The body misses keys at an attachment.")

            for attachment_data in declaration_data["attachments"]:
                data = attachment_data["file"].split(":")[0]
                mime = attachment_data["file"].split(":")[1].split(";")[0]
                base = attachment_data["file"].split(":")[1].split(";")[1].split(",")[0]

                if data != "data" or base != "base64":
                    give_error_response(self, 400, "Kan geen declaratie toevoegen. De opgestuurde bijlage gegevens "
                                                       "kloppen niet.",
                                        "The base64 string is incorrect.")

                if mime != "application/pdf" and mime.split("/")[0] != "image":
                    give_error_response(self, 400, "Kan geen declaratie toevoegen. Alleen pdf's of images zijn toegestaan.",
                                        "MimeType does not equal application/pdf or image/*", more_info=mime)

        # Post declaration
        declaration = ilmoitus_model.Declaration()
        declaration.class_name = "open_declaration"
        declaration.assigned_to = [assigned_to.key]
        declaration.created_by = created_by.key
        declaration.comment = declaration_data["comment"]
        declaration.items_count = 0
        declaration.items_total_price = 0
        declaration.put()

        posted_lines = []
        # Post declarationlines
        for line in declarationlines_data:
            newline = ilmoitus_model.DeclarationLine()

            try:
                newline.cost = int(line["cost"])
                declaration.items_count += 1
                declaration.items_total_price += newline.cost
            except Exception:
                give_error_response(self, 400, "De opgegeven data bevat foute waardes voor een declaratieline.",
                                "The body contains wrong values.")

            newline.receipt_date = dateutil.parser.parse(line["receipt_date"])
            newline.declaration_sub_type = ilmoitus_model.DeclarationSubType.get_by_id(int(line["declaration_sub_type"])).key
            newline.put()
            posted_lines.append(newline)

        declaration.lines = map(lambda line: line.key, posted_lines)
        declaration.put()

        posted_attachments = []
        if "attachments" in declaration_data:
            try:
                for attachment_data in declaration_data["attachments"]:
                    attachment = ilmoitus_model.Attachment()
                    attachment.declaration = declaration.key
                    attachment.name = attachment_data["name"]
                    attachment.file = attachment_data["file"]
                    attachment.put()
                    posted_attachments.append(attachment.get_object_as_data_dict())
            except Exception:
                give_error_response(self, 400, "Kan geen declaratie toevoegen. De opgestuurde data bevat foute "
                                               "waardes voor een bijlage.",
                                    "The body contains wrong values.")


        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), posted_lines)
        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines,
                                    'attachments': posted_attachments})

        response_module.give_response(self, combined_dict)


class SpecificDeclarationHandler(BaseRequestHandler):
    def get(self, declaration_id):
        if self.is_logged_in() and str.isdigit(declaration_id):
            result = ilmoitus_model.Declaration.get_by_id(long(declaration_id))

            if result is None:
                give_error_response(self, 404, "Kan de opgevraagde declaratie niet vinden",
                                    "Declaration id can only be of the type integer and cannot be None", 404)

            if len(result.lines) == 0:
                declarationline_query_result = []
            else:
                declarationline_query = ilmoitus_model.DeclarationLine.query(ilmoitus_model.DeclarationLine.key.IN(result.lines))
                declarationline_query_result = declarationline_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            if len(result.attachments) == 0:
                attachments_query_result = []
            else:
                attachments_query = ilmoitus_model.Attachment.query(ilmoitus_model.Attachment.key.IN(result.attachments))
                attachments_query_result = attachments_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            attachment_data = []
            for attachment in attachments_query_result:
                item = {"id": attachment.key.integer_id(), "name": attachment.name}
                attachment_data.append(item)

            data_dict = result.get_object_as_full_data_dict()
            data_dict["attachments"] = attachment_data
            data_dict["lines"] = map(lambda declaration_item: declaration_item.get_object_as_full_data_dict(), declarationline_query_result)

            current_user = self.logged_in_person()
            key = current_user.key

            if result.created_by == key:
                response_module.give_response(self, json.dumps(data_dict))

            elif current_user.class_name == 'supervisor':
                if key in result.assigned_to:
                    response_module.give_response(self, json.dumps(data_dict))
                else:
                    give_error_response(self, 401,
                                        "Deze declratie is niet aan jouw toegewezen", None, 401)

            elif current_user.class_name == 'human_resources' and result.class_name == \
                    'supervisor_approved_declaration' and result.submitted_to_human_resources_by is not None:
                response_module.give_response(self, json.dumps(data_dict))
            else:
                give_error_response(self, 401,
                                    "Je hebt niet de juiste rechten om deze declratie te openen", None, 401)
        # if declaration_id not is int
        else:
            give_error_response(self, 400, "Kan de opgevraagde declaratie niet vinden",
                                "Declaration id can only be of the type integer and cannot be None", 400)


class SpecificAttachmentHandler(BaseRequestHandler):
    def get(self, attachment_id):
        #TODO find a way to secure this (declaration nonce?)

        if str.isdigit(attachment_id):
            attachment = ilmoitus_model.Attachment.get_by_id(long(attachment_id))
            if attachment is None:
                    give_error_response(self, 404, "Kan de opgevraagde bijlage niet vinden.",
                                        "attachment id does not exist in the database.")
        else:
            give_error_response(self, 400, "Kan de opgevraagde bijlage niet vinden.",
                                "attachment id can only be of the type integer.")

        base64_string = attachment.file.split(",")[1]
        mime = attachment.file.split(":")[1].split(";")[0]

        self.response.headers['Content-Type'] = str(mime)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write(base64.b64decode(base64_string))
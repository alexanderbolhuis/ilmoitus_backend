__author__ = 'RobinB'

from error_checks import *
from response_module import *
from ilmoitus_model import *
from mail_module import *
from ilmoitus_auth import hash_secret, check_secret, gen_salt
import datetime
import mail_module
import dateutil.parser
import base64


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
        give_response(self, declaration.get_object_json_data())


class ForwardDeclarationHandler(BaseRequestHandler):
    def put(self, declaration_id):
        #Checks (break when fails)
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)

        is_declaration_states(self, declaration, {"locked_declaration", "open_declaration"})
        current_person = self.logged_in_person()

        #Checks (break when fails)
        is_declaration_assigned(self, declaration, current_person)
        assigned_to = has_post(self, "assigned_to", "nieuwe supervisor", break_if_missing=True)

        comment = has_post(self, "comment", "opmerking", break_if_missing=False)

        #Action
        new_supervisor = find_employee(self, assigned_to)
        is_current_person_supervisor(self, new_supervisor)
        declaration.assigned_to.append(new_supervisor.key)
        declaration.supervisor_comment = comment
        declaration.put()

        give_response(self, json.dumps(declaration.get_object_as_data_dict()))


class DeclineBySupervisorHandler(BaseRequestHandler):
    def put(self, declaration_id):
        #Checks (break when fails)
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)
        is_declaration_states(self, declaration, {"locked_declaration", "open_declaration"})

        current_person = self.logged_in_person()

        #Checks (break when fails)
        comment = has_post(self, "comment", "opmerking", break_if_missing=True)
        is_declaration_assigned(self, declaration, current_person)

        #Action
        declaration.class_name = "supervisor_declined_declaration"
        declaration.submitted_to_human_resources_by = current_person.key
        declaration.supervisor_declined_at = datetime.datetime.now()
        declaration.supervisor_comment = comment
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
        comment = has_post(self, "comment", "opmerking", break_if_missing=False)

        #Checks (break when fails)
        is_declaration_assigned(self, declaration, current_person)
        is_declaration_price_allowed_supervisor(self, declaration, current_person)

        #Action
        declaration.class_name = "supervisor_approved_declaration"
        declaration.submitted_to_human_resources_by = current_person.key
        declaration.supervisor_approved_at = datetime.datetime.now()

        declaration.supervisor_comment = comment  # comment will be None if none is given

        declaration.put()
        mail_module.send_message_declaration_status_changed(self, declaration)
        give_response(self, json.dumps(declaration.get_object_as_data_dict()))


class DeclineByHumanResourcesHandler(BaseRequestHandler):
    def put(self, declaration_id):
        #Checks (break when fails)
        self.is_logged_in()
        self.check_hr()
        comment = has_post(self, "comment", "opmerking", break_if_missing=False)

        declaration = find_declaration(self, declaration_id)
        is_declaration_state(self, declaration, {"supervisor_approved_declaration"})

        declaration.class_name = 'human_resources_declined_declaration'
        declaration.human_resources_declined_by = self.logged_in_person().key
        declaration.human_resources_declined_at = datetime.datetime.now()
        declaration.human_resources_comment = comment  # comment will be None if none is given
        declaration.put()

        send_message_declaration_status_changed(self, declaration)
        give_response(self, declaration.get_object_json_data())


class ApproveByHumanResourcesHandler(BaseRequestHandler):
    def put(self, declaration_id):
        #Checks (break when fails)
        self.is_logged_in()
        self.check_hr()
        declaration = find_declaration(self, declaration_id)
        is_declaration_state(self, declaration, {"supervisor_approved_declaration"})

        comment = has_post(self, "comment", "opmerking", break_if_missing=False)

        #Action
        declaration.class_name = "human_resources_approved_declaration"
        declaration.human_resources_approved_by = self.logged_in_person().key
        declaration.human_resources_approved_at = datetime.datetime.now()
        declaration.human_resources_comment = comment  # comment will be None if none is given
        declaration.put()

        send_message_declaration_status_changed(self, declaration)
        give_response(self, json.dumps(declaration.get_object_as_data_dict()))


class NewDeclarationHandler(BaseRequestHandler):
    def post(self):
        #Checks (break when fails)
        self.is_logged_in()

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
            sub_type = DeclarationSubType.get_by_id(int(line["declaration_sub_type"]))
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
        declaration = Declaration()
        declaration.class_name = "open_declaration"
        declaration.assigned_to = [assigned_to.key]
        declaration.created_by = self.logged_in_person().key
        declaration.comment = declaration_data["comment"]
        declaration.items_count = 0
        declaration.items_total_price = 0
        declaration.put()

        posted_lines = []
        # Post declarationlines
        for line in declarationlines_data:
            newline = DeclarationLine()

            try:
                newline.cost = int(line["cost"])
                declaration.items_count += 1
                declaration.items_total_price += newline.cost
            except Exception:
                give_error_response(self, 400, "De opgegeven data bevat foute waardes voor een declaratieline.",
                                "The body contains wrong values.")

            newline.receipt_date = dateutil.parser.parse(line["receipt_date"])
            newline.declaration_sub_type = DeclarationSubType.get_by_id(int(line["declaration_sub_type"])).key
            newline.put()
            posted_lines.append(newline)

        declaration.lines = map(lambda line: line.key, posted_lines)
        declaration.put()

        posted_attachments = []
        if "attachments" in declaration_data:
            try:
                for attachment_data in declaration_data["attachments"]:
                    attachment = Attachment()
                    attachment.declaration = declaration.key
                    attachment.name = attachment_data["name"]
                    attachment.file = attachment_data["file"]
                    attachment.put()
                    posted_attachments.append(attachment)
            except Exception:
                give_error_response(self, 400, "Kan geen declaratie toevoegen. De opgestuurde data bevat foute "
                                               "waardes voor een bijlage.",
                                    "The body contains wrong values.")

        declaration.attachments = map(lambda attachment: attachment.key, posted_attachments)
        declaration.put()

        data_dict = declaration.get_object_as_full_data_dict()
        give_response(self, json.dumps(data_dict))


class SpecificDeclarationHandler(BaseRequestHandler):
    def get(self, declaration_id):
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)
        current_user = self.logged_in_person()
        is_allowed_declaration_viewer(self, declaration, current_user)

        data_dict = declaration.get_object_as_full_data_dict()
        give_response(self, json.dumps(data_dict))

    def delete(self, declaration_id):
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)
        is_declaration_creator(self, declaration, self.logged_in_person())
        is_declaration_state(self, declaration, "open_declaration")

        ndb.delete_multi(declaration.lines)
        ndb.delete_multi(declaration.attachments)
        declaration.key.delete()

        give_response(self, json.dumps({'success': 'true'}))


class CreateAttachmentTokenHandler(BaseRequestHandler):
    def get(self, attachment_id):
        self.is_logged_in()
        attachment = find_attachment(self, attachment_id)
        declaration = find_declaration(self, attachment.declaration.integer_id())
        is_allowed_declaration_viewer(self, declaration, self.logged_in_person())

        #Generate token for view rights
        token = gen_salt(16)
        attachment.token = hash_secret(token)
        attachment.put()

        give_response(self, json.dumps({"attachment_token": token}))


class SpecificAttachmentHandler(BaseRequestHandler):
    def get(self, attachment_id, token):
        attachment = find_attachment(self, attachment_id)

        if check_secret(token, attachment.token):
            base64_string = attachment.file.split(",")[1]
            mime = attachment.file.split(":")[1].split(";")[0]

            self.response.headers['Content-Type'] = str(mime)
            self.response.headers['Access-Control-Allow-Origin'] = '*'
            self.response.write(base64.b64decode(base64_string))
        else:
            auth_error(self)

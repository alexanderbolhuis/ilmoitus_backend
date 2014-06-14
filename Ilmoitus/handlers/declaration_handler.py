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
        is_declaration_assigned(self, declaration, self.logged_in_person())
        is_declaration_state(self, declaration, "open_declaration")

        #Action
        declaration.locked_at = datetime.datetime.now()
        declaration.class_name = "locked_declaration"
        declaration.put()
        send_message_declaration_status_changed(self, declaration)

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
        is_declaration_state(self, declaration, "supervisor_approved_declaration")

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
        is_declaration_state(self, declaration, "supervisor_approved_declaration")

        comment = has_post(self, "comment", "opmerking", break_if_missing=False)
        will_be_payed_out_on = has_post(self, "will_be_payed_out_on", "datum van uitbetaling", break_if_missing=True)
        will_be_payed_out_on_date = datetime.datetime.strptime(will_be_payed_out_on, "%m-%Y")
        #Action
        declaration.class_name = "human_resources_approved_declaration"
        declaration.human_resources_approved_by = self.logged_in_person().key
        declaration.human_resources_approved_at = datetime.datetime.now()
        declaration.human_resources_comment = comment  # comment will be None if none is given
        declaration.will_be_payed_out_on = will_be_payed_out_on_date
        declaration.put()
        send_mail_declaration_approved(self, declaration)

        give_response(self, json.dumps(declaration.get_object_as_data_dict()))


class NewDeclarationHandler(BaseRequestHandler):
    def post(self):
        self.is_logged_in()
        declaration_data = has_post(self, "declaration", "declaratie", True, False)
        is_complete_dict(self, declaration_data, ["lines", "supervisor"], "declaration")

        declaration_lines_data = declaration_data["lines"]
        assigned_to = find_employee(self, declaration_data["supervisor"])
        if_employee_is_supervisor(self, assigned_to)

        if "attachments" in declaration_data.keys():
            declaration_attachments_data = declaration_data["attachments"]
        else:
            declaration_attachments_data = []

        #Check lines and attachments
        for line in declaration_lines_data:
            is_complete_dict(self, line, ["receipt_date", "cost", "declaration_sub_type"], "declaration line")
            convert_to_float(self, line["cost"])
            find_declaration_sub_type(self, line["declaration_sub_type"])

        for attachment_data in declaration_attachments_data:
            is_complete_dict(self, attachment_data, ["name", "file"], "declaration attachment")
            is_valid_declaration_attachment(self, attachment_data)

        # Post declaration
        declaration = Declaration()
        declaration.class_name = "open_declaration"
        declaration.assigned_to = [assigned_to.key]
        declaration.created_by = self.logged_in_person().key
        if "comment" in declaration_data.keys():
            declaration.comment = declaration_data["comment"]
        else:
            declaration.comment = ""
        declaration.items_count = 0
        declaration.items_total_price = 0
        declaration.put()

        #Save lines / attachments
        for line in declaration_lines_data:
            newline = DeclarationLine()
            newline.cost = convert_to_float(self, line["cost"])
            newline.receipt_date = dateutil.parser.parse(line["receipt_date"])
            newline.declaration_sub_type = DeclarationSubType.get_by_id(long(line["declaration_sub_type"])).key
            if "comment" in line.keys():
                newline.comment = line["comment"]
            newline.put()

            declaration.items_count += 1
            declaration.items_total_price += newline.cost
            declaration.lines.append(newline.key)

        for attachment_data in declaration_attachments_data:
            attachment = Attachment()
            attachment.declaration = declaration.key
            attachment.name = attachment_data["name"]
            attachment.file = attachment_data["file"]
            attachment.put()
            declaration.attachments.append(attachment.key)

        declaration.put()
        send_mail_new_declaration_submitted(self, declaration)

        give_response(self, json.dumps(declaration.get_object_as_full_data_dict()))


class SpecificDeclarationHandler(BaseRequestHandler):
    def get(self, declaration_id):
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)
        current_user = self.logged_in_person()
        is_allowed_declaration_viewer(self, declaration, current_user)

        data_dict = declaration.get_object_as_full_data_dict()
        give_response(self, json.dumps(data_dict))

    #TODO: Unittest
    def delete(self, declaration_id):
        self.is_logged_in()
        declaration = find_declaration(self, declaration_id)
        is_declaration_creator(self, declaration, self.logged_in_person())
        is_declaration_state(self, declaration, "open_declaration")

        ndb.delete_multi(declaration.lines)
        ndb.delete_multi(declaration.attachments)
        declaration.key.delete()

        give_response(self, json.dumps({'success': 'true'}))

    #TODO: Unittest
    def put(self, declaration_id):
        self.is_logged_in()

        #Check requested declaration
        declaration = find_declaration(self, declaration_id)
        is_declaration_creator(self, declaration, self.logged_in_person())
        is_declaration_state(self, declaration, "open_declaration")

        #Check received declaration data
        declaration_data = has_post(self, "declaration", "declaratie", True, False)
        is_complete_dict(self, declaration_data, ["lines", "supervisor"], "declaration")
        assigned_to = find_employee(self, declaration_data["supervisor"])
        if_employee_is_supervisor(self, assigned_to)

        declaration_lines_data = declaration_data["lines"]
        if "attachments" in declaration_data.keys():
            declaration_attachments_data = declaration_data["attachments"]
        else:
            declaration_attachments_data = []

        #Check lines and attachments
        for line in declaration_lines_data:
            is_complete_dict(self, line, ["receipt_date", "cost", "declaration_sub_type"], "declaration line")
            find_declaration_sub_type(self, line["declaration_sub_type"])
            convert_to_float(self, line["cost"])

        for attachment_data in declaration_attachments_data:
            if "id" not in attachment_data.keys() or attachment_data["id"] == "0":
                is_complete_dict(self, attachment_data, ["name", "file"], "declaration attachment")
                is_valid_declaration_attachment(self, attachment_data)
            else:
                is_complete_dict(self, attachment_data, ["name", "id"], "declaration attachment")

        # Reset declaration
        if "comment" in declaration_data.keys():
            declaration.comment = declaration_data["comment"]
        else:
            declaration.comment = ""
        declaration.items_count = 0
        declaration.items_total_price = 0
        declaration.assigned_to = [assigned_to.key]
        declaration.lines = []
        declaration.put()

        # Lines (Delete all / Add)
        ndb.delete_multi(declaration.lines)
        for line in declaration_lines_data:
            newline = DeclarationLine()
            newline.cost = convert_to_float(self, line["cost"])
            newline.receipt_date = dateutil.parser.parse(line["receipt_date"])
            newline.declaration_sub_type = DeclarationSubType.get_by_id(long(line["declaration_sub_type"])).key
            if "comment" in line.keys():
                newline.comment = line["comment"]

            newline.put()

            declaration.items_count += 1
            declaration.items_total_price += newline.cost
            declaration.lines.append(newline.key)

        # Attachments (Add / Delete)
        attachments = []
        for attachment_id in declaration.attachments:
            found = False
            for attachment_data in declaration_attachments_data:
                if "id" in attachment_data.keys() and str(attachment_data["id"]) == str(attachment_id.integer_id()):
                    found = True

            if not found:
                ndb.delete(attachment_id)
            else:
                attachments.append(attachment_id)

        for attachment_data in declaration_attachments_data:
            if "file" in attachment_data.keys() and attachment_data["file"] != "":
                attachment = Attachment()
                attachment.declaration = declaration.key
                attachment.name = attachment_data["name"]
                attachment.file = attachment_data["file"]
                attachment.put()
                attachments.append(attachment.key)

        declaration.attachments = attachments
        declaration.put()
        give_response(self, json.dumps(declaration.get_object_as_full_data_dict()))


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

            #clear token
            attachment.token = ""
            attachment.put()

            self.response.headers['Content-Type'] = str(mime)
            self.response.headers['Access-Control-Allow-Origin'] = '*'
            self.response.write(base64.b64decode(base64_string))
        else:
            auth_error(self)

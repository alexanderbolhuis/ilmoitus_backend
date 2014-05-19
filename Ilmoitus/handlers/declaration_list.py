__author__ = 'RobinB'

from ilmoitus_auth import *
from response_module import *
import base64

class AllDeclarationsForEmployeeHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            query = Declaration.query(Declaration.created_by == self.logged_in_person().key)
            response_module.respond_with_object_collection_with_query(self, query)


class AllDeclarationsForSupervisorHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            declaration_query = Declaration.query(Declaration.class_name == 'open_declaration',
                                                  Declaration.assigned_to == self.logged_in_person().key)
            response_module.respond_with_object_collection_with_query(self, declaration_query)


class AllDeclarationsForHumanResourcesHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            #TODO: check if user is hr (maybe it already works?)
            if self.logged_in_person().class_name == "human_resources":  # person.key.class_name == "human_resources":
                declaration_query = Declaration.query(Declaration.class_name == "supervisor_approved_declaration")
                response_module.respond_with_object_collection_with_query(self, declaration_query)
            else:
                give_error_response(self, 401, "De declaraties kunnen niet worden opgehaald omdat u niet "
                                               "de juiste permissies heeft.",
                                               "current_user not from human_resources")


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
        person_data = ilmoitus_auth.get_current_person(self)
        current_user = person_data["person_value"]

        if current_user is None:
            give_error_response(self, 401, "De bijlage kan niet worden opgehaald omdat u niet "
                                           "de juiste permissies heeft.",
                                "current_user is None")

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
        self.response.headers['Content-Type'] = mime
        self.response.write(base64.b64decode(base64_string))
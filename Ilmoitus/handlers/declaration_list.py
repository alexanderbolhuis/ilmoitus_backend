__author__ = 'RobinB'

from ilmoitus_auth import *
from response_module import *


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
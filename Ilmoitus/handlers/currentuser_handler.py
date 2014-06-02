__author__ = 'RobinB'

from ilmoitus_auth import *
from response_module import *
from ilmoitus_model import *


class CurrentUserDetailsHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            person = self.logged_in_person()
            give_response(self, person.get_object_json_data())


class CurrentUserSettingsHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            #TODO make this function
            pass

    def put(self):
        if self.is_logged_in():
            #TODO make this function
            pass


class CurrentUserSupervisorsHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            logged_in_person = self.logged_in_person()
            supervisor = logged_in_person.supervisor
            if supervisor is None:
                supervisor_query = Person.query(Person.class_name == "supervisor", logged_in_person.key != Person.key)
                query_result = supervisor_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())
            else:
                supervisor_query = Person.query(Person.class_name == "supervisor", supervisor == Person.key)
                supervisor_query2 = Person.query(Person.class_name == "supervisor", supervisor != Person.key, logged_in_person.key != Person.key)
                query_result = supervisor_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset()) + supervisor_query2.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            respond_with_existing_model_object_collection(self, query_result)


class CurrentUserAssociatedDeclarationsHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            key = self.logged_in_person().key
            query = Declaration.query(ndb.OR(Declaration.created_by == key,
                                             Declaration.assigned_to == key,
                                             Declaration.supervisor_approved_by == key,
                                             Declaration.submitted_to_human_resources_by == key,
                                             Declaration.human_resources_declined_by == key,
                                             Declaration.human_resources_approved_by == key,
                                             Declaration.declined_by == key))

            respond_with_object_collection_with_query(self, query)
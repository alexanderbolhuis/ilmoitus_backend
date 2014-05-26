__author__ = 'RobinB'

from ilmoitus_auth import *
from response_module import *
import datetime
import mail_module
import dateutil.parser


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
        #TODO now this function gets all supervisors, we need to know if it only need supervisors of current person
        if self.is_logged_in():
            supervisor_query = ilmoitus_model.Person.query(Person.class_name == "supervisor")
            respond_with_object_collection_with_query(self, supervisor_query)


class CurrentUserAssociatedDeclarationsHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            key = self.logged_in_person().key
            query = Declaration.query(ndb.OR(Declaration.created_by == key,
                                             Declaration.assigned_to == key,  # TODO fix the list search
                                             Declaration.supervisor_approved_by == key,
                                             Declaration.submitted_to_human_resources_by == key,
                                             Declaration.human_resources_declined_by == key,
                                             Declaration.human_resources_approved_by == key,
                                             Declaration.declined_by == key))

            respond_with_object_collection_with_query(self, query)
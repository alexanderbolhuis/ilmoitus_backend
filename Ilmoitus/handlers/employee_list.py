__author__ = 'RobinB'

from ilmoitus_auth import *
from response_module import *
from mail_module import *
import datetime
import mail_module
import dateutil.parser


class AllEmployeesHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            respond_with_object_collection_by_class(self,
                                                    Person,
                                                    self.get_header_limit(),
                                                    self.get_header_offset())


class SpecificEmployeeDetailsHandler(BaseRequestHandler):
    def get(self, employee_id):
        if self.is_logged_in():
            #TODO check if user is allowed to see this data (discussion needed)
            respond_with_object_details_by_id(self, Person, employee_id)


class SpecificEmployeeTotalDeclarationsHandler(BaseRequestHandler):
    def get(self, employee_id):
        # Only supervisors can perform the actions in this handler: check for that first
        current_person_data = ilmoitus_auth.get_current_person(self)
        if "user_is_logged_in" not in current_person_data.keys() or \
                not current_person_data["user_is_logged_in"]:  # if logged in is false
            give_error_response(self, 401,
                                "Er is niemand ingelogd.",
                                "get_current_person returned a False value for user_is_logged_in")

        current_person_object = current_person_data["person_value"]
        if current_person_object is None:
            give_error_response(self, 401, "De ingelogd persoon in onbekend binnen de applicatie"
                                           " of de ingelogde persoon heeft niet de rechten van een"
                                           " leidinggevende binnen de applicatie.",
                                "person_value key in get_current_person was None")

        # Does employee exist
        employee = ilmoitus_model.Person.get_by_id(int(employee_id))
        if employee is None:
            give_error_response(self, 404, "Werknemer bestaat niet",
                                            "Employee not found")

        # Find declarations for employee
        accepted_declarations = ilmoitus_model.Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="human_resources_approved_declaration").fetch()
        accepted = len(accepted_declarations)

        open_declarations = ilmoitus_model.Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="open_declaration").fetch()
        open = len(open_declarations)

        sv_denied_declarations = ilmoitus_model.Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="supervisor_declined_declaration").fetch()
        sv_denied = len(sv_denied_declarations)

        hr_denied_declarations = ilmoitus_model.Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="human_resources_declined_declaration").fetch()
        hr_denied = len(hr_denied_declarations)

        total_cost = 0

        for declaration in accepted_declarations:
            total_cost = total_cost + declaration.items_total_price

        response_dict = {"id": employee_id, "open_declarations": open, "accepted_declarations": accepted, "denied_declarations": (hr_denied + sv_denied), "total_declarated_price": total_cost}
        response_module.give_response(self, json.dumps(response_dict))
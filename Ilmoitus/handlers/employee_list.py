__author__ = 'RobinB'

from error_checks import *


class AllEmployeesHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            respond_with_object_collection_with_query(self, Person.query())


class SpecificEmployeeDetailsHandler(BaseRequestHandler):
    def get(self, employee_id):
        if self.is_logged_in():
            respond_with_object_details_by_id(self, Person, employee_id)


class SpecificEmployeeTotalDeclarationsHandler(BaseRequestHandler):
    def get(self, employee_id):
        if self.is_logged_in():
            # Does employee exist
            employee = find_employee(self, employee_id)

            # Find declarations for employee
            accepted_declarations = Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="human_resources_approved_declaration").fetch()
            accepted = len(accepted_declarations)

            open_declarations = Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="open_declaration").fetch()
            open = len(open_declarations)

            sv_denied_declarations = Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="supervisor_declined_declaration").fetch()
            sv_denied = len(sv_denied_declarations)

            hr_denied_declarations = Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="human_resources_declined_declaration").fetch()
            hr_denied = len(hr_denied_declarations)

            total_cost = 0
            for declaration in accepted_declarations:
                total_cost += declaration.items_total_price

            response_dict = {"id": employee_id, "open_declarations": open, "accepted_declarations": accepted, "denied_declarations": (hr_denied + sv_denied), "total_declarated_price": total_cost}
            give_response(self, json.dumps(response_dict))
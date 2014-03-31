__author__ = 'Sjors van Lemmen'
import ilmoitus_model
import random
from datetime import datetime, date


class PersonDataCreator():
    def __init__(self):
        pass

    @staticmethod
    def create_valid_person_data(email_added_id):
        person = ilmoitus_model.Person()
        person.class_name = "user"
        person.first_name = "Rogier"
        person.last_name = "Boleij"
        person.email = "r.boleij" + str(email_added_id) + "@gmail.com"
        person.wants_email_notifications = bool(random.randint(0, 1))
        person.wants_phone_notifications = not bool(person.wants_email_notifications)

        person.put()
        return person

    @staticmethod
    def create_valid_employee_data(employee_number=0):
        employee = ilmoitus_model.Person()
        department = DepartmentDataCreator.create_valid_department()
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee_number + 1)

        employee.class_name = "employee"
        employee.supervisor = supervisor.key
        employee.department = department.key
        employee.employee_number = employee_number
        employee.put()
        return employee

    @staticmethod
    def create_valid_supervisor(supervisors_supervisor=None, employee_number=0):
        supervisor = ilmoitus_model.Person()
        supervisor.class_name = "supervisor"
        supervisor.department = DepartmentDataCreator.create_valid_department().key
        if supervisors_supervisor is not None:
            supervisor.supervisor = supervisors_supervisor.key
        supervisor.employee_number = employee_number
        supervisor.put()
        return supervisor

    @staticmethod
    def create_valid_human_resource(human_resources_human_resource=None, employee_number=0):
        human_resource = ilmoitus_model.Person()
        human_resource.class_name = "human_resources"
        human_resource.department = DepartmentDataCreator.create_valid_department().key
        if human_resources_human_resource is not None:
            human_resource.human_resource = human_resources_human_resource.key
        human_resource.employee_number = employee_number
        human_resource.put()
        return human_resource


class DepartmentDataCreator():
    def __init__(self):
        pass

    @staticmethod
    def create_valid_department(department_name="Human Resources"):
        department = ilmoitus_model.Department()
        department.name = department_name
        department.put()
        return department


class DeclarationsDataCreator():
    def __init__(self):
        pass

    @staticmethod
    def create_valid_declaration_lines(declaration, amount_of_lines):
        declaration_type = DeclarationsDataCreator.create_valid_declaration_type()
        subtype = DeclarationsDataCreator.create_valid_declaration_sub_type_without_max_cost(declaration_type)

        lines = []

        for i in range(0, amount_of_lines):
            line = ilmoitus_model.DeclarationLine()
            line.declaration = declaration.key
            line.declaration_sub_type = subtype
            line.cost = random.randint(0,100)
            line.put()

            lines.append(line)

        return lines

    @staticmethod
    def create_valid_declaration_type():
        type = ilmoitus_model.DeclarationType()
        type.name = "reiskosten"

        type.put()

        return type

    @staticmethod
    def create_valid_declaration_sub_type_without_max_cost(declaration_type):
        sub_type = ilmoitus_model.DeclarationSubType()
        sub_type.declaration_super_type = declaration_type.key
        sub_type.name = "tanken"

        sub_type.put()

        return sub_type

    @staticmethod
    def create_valid_declaration_sub_type_with_max_cost(declaration_type):
        sub_type = ilmoitus_model.DeclarationSubType()
        sub_type.declaration_super_type = declaration_type.key
        sub_type.name = "openbaar vervoer"
        sub_type.max_cost = 101

        sub_type.put()

        return sub_type


    @staticmethod
    def create_valid_open_declaration(employee, supervisor):
        employee_key = employee.key
        supervisor_key = supervisor.key

        employee.supervisor = supervisor_key

        open_declaration = ilmoitus_model.Declaration()
        open_declaration.class_name = "open_declaration"
        open_declaration.created_by = employee_key
        open_declaration.assigned_to = supervisor_key
        open_declaration.comment = "Thanks for taking care of this for me!"

        open_declaration.put()
        return open_declaration

    @staticmethod
    def create_valid_approved_declaration(employee, supervisor):
        employee_key = employee.key

        open_declaration = ilmoitus_model.Declaration()
        open_declaration.class_name = "human_resources_approved_declaration"
        open_declaration.created_at = datetime.now()
        open_declaration.created_by = employee.key
        open_declaration.assigned_to = supervisor.key
        open_declaration.locked_at = datetime.now()
        open_declaration.comment = "Thanks for taking care of this for me!"
        open_declaration.approved_by = supervisor.key
        open_declaration.supervisor_approved_at = datetime.now()
        open_declaration.sent_to_human_resources_at = datetime.now()
        open_declaration.supervisor_comment = "No problem!"
        open_declaration.human_resources_comment = "No comment on this!"
        open_declaration.will_be_payed_out_on = date.today()
        open_declaration.submitted_to_human_resources_by = supervisor.key
        open_declaration.put()
        return open_declaration

    @staticmethod
    def create_valid_supervisor_approved_declaration(employee, supervisor):
        employee_key = employee.key

        open_declaration = ilmoitus_model.Declaration()
        open_declaration.class_name = "supervisor_approved_declaration"
        open_declaration.created_at = datetime.now()
        open_declaration.created_by = employee.key
        open_declaration.assigned_to = supervisor.key
        open_declaration.locked_at = datetime.now()
        open_declaration.comment = "Thanks for taking care of this for me!"
        open_declaration.approved_by = supervisor.key
        open_declaration.supervisor_approved_at = datetime.now()
        open_declaration.sent_to_human_resources_at = datetime.now()
        open_declaration.supervisor_comment = "No problem!"
        open_declaration.submitted_to_human_resources_by = supervisor.key
        open_declaration.put()
        return open_declaration

    @staticmethod
    def create_valid_locked_declaration(employee, supervisor):
        employee_key = employee.key
        supervisor_key = supervisor.key

        employee.supervisor = supervisor_key

        locked_declaration = ilmoitus_model.Declaration()
        locked_declaration.class_name = "closed_declaration"
        locked_declaration.created_by = employee_key
        locked_declaration.assigned_to = supervisor_key
        locked_declaration.comment = "Thanks for taking care of this for me!"

        locked_declaration.put()
        return locked_declaration

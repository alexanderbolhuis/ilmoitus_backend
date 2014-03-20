__author__ = 'Sjors van Lemmen'
import model
import random


class PersonDataCreator():
    def __init__(self):
        pass

    @staticmethod
    def create_valid_person_data(email_added_id):
        person = model.User()
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
        employee = model.User()
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
        supervisor = model.User()
        supervisor.class_name = "supervisor"
        supervisor.department = DepartmentDataCreator.create_valid_department().key
        if supervisors_supervisor is not None:
            supervisor.supervisor = supervisors_supervisor.key
        supervisor.employee_number = employee_number
        supervisor.put()
        return supervisor

    @staticmethod
    def create_valid_human_resource(human_resources_human_resource=None, employee_number=0):
        human_resource = model.User()
        human_resource.class_name = "human_resource"
        human_resource.department = DepartmentDataCreator.create_valid_department().key
        if human_resources_human_resource is not None:
            human_resource.human_resource = human_resources_human_resource.key
        human_resource.employee_number = employee_number
        human_resource.put
        return human_resource


class DepartmentDataCreator():
    def __init__(self):
        pass

    @staticmethod
    def create_valid_department(department_name="Human Resources"):
        department = model.Department()
        department.name = department_name
        department.put()
        return department


class DeclarationsDataCreator():
    def __init__(self):
        pass

    @staticmethod
    def create_valid_open_declaration(employee, supervisor):
        employee_key = employee.key
        supervisor_key = supervisor.key

        employee.supervisor = supervisor_key

        open_declaration = model.Declaration()
        open_declaration.class_name = "open_declaration"
        open_declaration.created_by = employee_key
        open_declaration.assigned_to = supervisor_key
        open_declaration.comment = "Thanks for taking care of this for me!"

        open_declaration.put()
        return open_declaration

    @staticmethod
    def create_valid_approved_declaration(employee, human_resource):
        employee_key = employee.key
        human_resource_key = human_resource.key

        employee.human_resource = human_resource_key

        open_declaration = model.Declaration()
        open_declaration.class_name = "approved_declaration"
        open_declaration.created_by = employee_key
        open_declaration.assigned_to = human_resource_key
        open_declaration.comment = "Thanks for taking care of this for me!"

        open_declaration.put()
        return open_declaration

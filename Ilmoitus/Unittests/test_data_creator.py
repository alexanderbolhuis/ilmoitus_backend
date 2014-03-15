__author__ = 'Sjors van Lemmen'
import model


class PersonDataCreator():
    def __init__(self):
        pass

    @staticmethod
    def create_valid_person_data(email_added_id):
        person = model.User()
        person.first_name = "Rogier"
        person.last_name = "Boleij"
        person.email = "r.boleij" + str(email_added_id) + "@gmail.com"
        person.class_name = "person"

        person.put()
        return person

    @staticmethod
    def create_valid_employee_data(employee_number=0):
        employee = model.User()
        department = PersonDataCreator.create_valid_department()
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee_number + 1)

        employee.supervisor = supervisor.key
        employee.department = department.key
        employee.employee_number = employee_number
        employee.class_name = "employee"
        employee.put()
        return employee

    @staticmethod
    def create_valid_supervisor(supervisors_supervisor=None, employee_number=0):
        supervisor = model.User()
        supervisor.department = PersonDataCreator.create_valid_department().key
        if supervisors_supervisor is not None:
            supervisor.supervisor = supervisors_supervisor.key
        supervisor.employee_number = employee_number
        supervisor.class_name = "supervisor"
        supervisor.put()
        return supervisor

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
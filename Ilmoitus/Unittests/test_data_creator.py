__author__ = 'Sjors van Lemmen'
import model
import random


class PersonDataCreator():
    def __init__(self):
        pass

    @staticmethod
    def create_valid_person_data(email_added_id):
        person = model.Person()
        person.first_name = "Rogier"
        person.last_name = "Boleij"
        person.email = "r.boleij" + str(email_added_id) + "@gmail.com"

        person.put()
        return person

    @staticmethod
    def create_valid_employee_data(employee_number=0):
        employee = model.Employee()
        department = PersonDataCreator.create_valid_department()
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee_number + 1)

        employee.supervisor = supervisor.key
        employee.department = department.key
        employee.employee_number = employee_number
        employee.wants_email_notifications = bool(random.randint(0, 1))
        employee.wants_phone_notifications = not bool(employee.wants_email_notifications)
        employee.put()
        return employee

    @staticmethod
    def create_valid_supervisor(supervisors_supervisor=None, employee_number=0):
        supervisor = model.Supervisor()
        supervisor.department = PersonDataCreator.create_valid_department().key
        if supervisors_supervisor is not None:
            supervisor.supervisor = supervisors_supervisor.key
        supervisor.employee_number = employee_number
        supervisor.put()
        return supervisor

    @staticmethod
    def create_valid_department(department_name="Human Resources"):
        department = model.Department()
        department.name = department_name
        department.put()
        return department
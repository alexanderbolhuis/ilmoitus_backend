__author__ = 'Sjors van Lemmen'
import model
import base.base_test_methods as base_test_module


class PersonDataCreator(base_test_module.BaseTestClass):
    def create_valid_employee_data(self, employee_number=0):
        employee = model.Employee()
        department = self.create_valid_department()
        supervisor = self.create_valid_supervisor(employee_number + 1)

        employee.supervisor = supervisor
        employee.department = department
        employee.employee_number = employee_number
        employee.put()
        return employee

    def create_valid_supervisor(self, supervisors_supervisor=None, employee_number=0):
        supervisor = model.Supervisor()
        supervisor.department = self.create_valid_department()
        supervisor.supervisor = supervisors_supervisor
        supervisor.employee_number = employee_number
        supervisor.put()
        return supervisor

    def create_valid_department(self, department_name="Human Resources"):
        department = model.Department()
        department.name = department_name
        department.put()
        return department
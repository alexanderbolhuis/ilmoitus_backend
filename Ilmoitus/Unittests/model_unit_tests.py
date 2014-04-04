__author__ = 'Sjors van Lemmen'

import random
from Base.base_test_methods import BaseTestClass
from test_data_creator import DeclarationsDataCreator, PersonDataCreator, DepartmentDataCreator


class ModelTest(BaseTestClass):
    def test_open_declaration_can_set_own_properties(self):
        self.setup_test_server_without_handlers()

        employee = PersonDataCreator.create_valid_employee_data(0)
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee.key.integer_id() + 1)
        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)

        self.assertEqual(open_declaration.created_by, employee.key)
        self.assertEqual(open_declaration.assigned_to[0], supervisor.key)

    def test_open_declaration_cant_set_other_properties_than_permitted(self):
        self.setup_test_server_without_handlers()

        employee = PersonDataCreator.create_valid_employee_data(0)
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee.key.integer_id() + 1)
        hr_employee = PersonDataCreator.create_valid_person_data(random.randint(3, 100))

        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)

        open_declaration.submitted_to_human_resources_by = hr_employee

        self.assertEqual(open_declaration.created_by, employee.key)
        self.assertEqual(open_declaration.assigned_to[0], supervisor.key)

        self.assertIsNone(open_declaration.submitted_to_human_resources_by)

    def test_declaration_class_name_to_readable_string(self):
        self.setup_test_server_without_handlers()

        employee = PersonDataCreator.create_valid_employee_data(0)
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee.key.integer_id() + 1)
        hr_employee = PersonDataCreator.create_valid_person_data(random.randint(3, 100))

        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)

        self.assertEqual(open_declaration.readable_state(), "Open")

    def test_person_can_set_own_properties(self):
        self.setup_test_server_without_handlers()

        person = PersonDataCreator.create_valid_person_data(1)

        first_name = "Olaf"
        last_name = "Jansen"
        email = "ojansen@gmail.com"
        person.first_name = first_name
        person.last_name = last_name
        person.email = email

        self.assertEqual(person.first_name, first_name)
        self.assertEqual(person.last_name, last_name)
        self.assertEqual(person.email, email)

    def test_person_cant_set_other_properties_than_permitted(self):
        self.setup_test_server_without_handlers()

        department = DepartmentDataCreator.create_valid_department()
        person = PersonDataCreator.create_valid_person_data(1)
        employee_number = 12984

        person.department = department.key
        person.employee_number = employee_number

        self.assertIsNone(person.department)
        self.assertIsNone(person.employee_number)

    def test_employee_can_set_own_properties(self):
        self.setup_test_server_without_handlers()

        employee = PersonDataCreator.create_valid_employee_data(1)

        first_name = "Olaf"
        last_name = "Jansen"
        email = "ojansen@gmail.com"
        employee_number = 238012
        department_key = DepartmentDataCreator.create_valid_department().key
        supervisor_key = PersonDataCreator.create_valid_supervisor(None, employee.key.integer_id()).key

        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.employee_number = employee_number
        employee.department = department_key
        employee.supervisor = supervisor_key

        self.assertEqual(employee.first_name, first_name)
        self.assertEqual(employee.last_name, last_name)
        self.assertEqual(employee.email, email)
        self.assertEqual(employee.employee_number, employee_number)
        self.assertEqual(employee.department, department_key)
        self.assertEqual(employee.supervisor, supervisor_key)

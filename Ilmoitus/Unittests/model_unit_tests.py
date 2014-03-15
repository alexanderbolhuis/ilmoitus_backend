__author__ = 'Sjors van Lemmen'

import random
from Base.base_test_methods import BaseTestClass
from test_data_creator import DeclarationsDataCreator, PersonDataCreator


class ModelTest(BaseTestClass):
    def test_open_declaration_can_set_own_properties(self):
        self.setup_dummy_server_without_handlers()

        employee = PersonDataCreator.create_valid_employee_data(0)
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee.key.integer_id() + 1)
        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)

        self.assertEqual(open_declaration.created_by, employee.key)
        self.assertEqual(open_declaration.assigned_to, supervisor.key)

    def test_open_declaration_cant_set_other_properties_than_permitted(self):
        self.setup_dummy_server_without_handlers()

        employee = PersonDataCreator.create_valid_employee_data(0)
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee.key.integer_id() + 1)
        hr_employee = PersonDataCreator.create_valid_person_data(random.randint(3, 100))

        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)

        open_declaration.submitted_to_hr_by = hr_employee

        self.assertEqual(open_declaration.created_by, employee.key)
        self.assertEqual(open_declaration.assigned_to, supervisor.key)

        self.assertIsNone(open_declaration.submitted_to_hr_by)
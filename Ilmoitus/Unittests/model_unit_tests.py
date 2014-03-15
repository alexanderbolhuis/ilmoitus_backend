__author__ = 'Sjors van Lemmen'

import model
import time
from Base.base_test_methods import BaseTestClass
from test_data_creator import DeclarationsDataCreator, PersonDataCreator


class ModelTest(BaseTestClass):
    def test_open_declaration_can_set_own_propperties(self):
        employee = PersonDataCreator.create_valid_employee_data(0)
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee.key.integer_id())
        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        try:
            open_declaration.created_at = time.time()
            open_declaration.created_by = 3
            open_declaration.assigned_to = 1
            open_declaration.comment = "testing if this is the new comment"

        except AttributeError:
            self.fail("permission Error")

    def test_open_declaration_can_set_other_properties(self):
        employee = PersonDataCreator.create_valid_employee_data(0)
        supervisor = PersonDataCreator.create_valid_supervisor(None, employee.key.integer_id())
        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)

        open_declaration.created_at = time.time()
        open_declaration.created_by = 3
        open_declaration.assigned_to = supervisor.key.integer_id()
        open_declaration.comment = "testing if this is the new comment"
        self.assertRaises(AttributeError, supervisor.key.integer_id())  # should fail on this method
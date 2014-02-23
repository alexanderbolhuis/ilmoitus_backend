__author__ = 'Sjors van Lemmen'
import random
import ilmoitus as main_application
from test_data_creator import PersonDataCreator


class EmployeeHandlerTest(PersonDataCreator):
    def test_get_all_employee_positive(self):
        self.set_up_custom_path([("/employees", main_application.AllEmployeesHandler)])
        number_of_employees = random.randint(1, 10)
        for i in range(0, number_of_employees):
            employee = self.create_valid_employee_data(i)
            self.assertTrue(employee is not None)

    def test_get_all_employee_negative_no_employees(self):
        self.assertFalse(1 == 2)

    def test_get_all_employee_negative_no_persons(self):
        self.assertFalse(1 == 2)
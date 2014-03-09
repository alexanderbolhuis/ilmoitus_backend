__author__ = 'Sjors van Lemmen'
import random
import json
import ilmoitus as main_application
from test_data_creator import PersonDataCreator
from Base.base_test_methods import BaseTestClass


class EmployeeHandlerTest(BaseTestClass):
    def test_get_all_employee_positive(self):
        path = "/employees"
        self.set_up_custom_path([(path, main_application.AllEmployeesHandler)])
        number_of_employees = random.randint(1, 10)
        for i in range(0, number_of_employees):
            PersonDataCreator.create_valid_employee_data(i)

        self.positive_test_stub_handler(path, "get")

    def test_get_all_employee_negative_no_employees(self):
        """
         This test will test specifically if there are no employees. This means that there will be (some) objects
         of it's superclass Person, but none that match on the Employee class.
        """
        path = "/employees"
        self.set_up_custom_path([(path, main_application.AllEmployeesHandler)])
        number_of_persons = random.randint(1, 10)
        for i in range(0, number_of_persons):
            PersonDataCreator.create_valid_person_data(i)

        self.negative_test_stub_handler(path, "get", 404)

    def test_get_all_employee_negative_no_persons(self):
        """
         This test will test if the right error is given when there are no persons whatsoever.
        """
        path = "/employees"
        self.set_up_custom_path([(path, main_application.AllEmployeesHandler)])

        self.negative_test_stub_handler(path, "get", 404)


class AuthorizationStatusHandler(BaseTestClass):
    """
        These tests all rely on the users API, and therefore in each test, the users stub will be initialized along
        the memcache and datastore stub.

        This test consists of several parts: one that checks for a user that is logged in but not an admin,
        one that checks for when a user is not logged in (admin is then unknown) and one that checks for when
        a user is logged in AND is an admin.
    """

    def setup_user_data(self, user_is_logged_in, user_is_admin):
        """
            Helper method to set-up all data needed in these unit tests.

            :param user_is_logged_in: Boolean that indicates whether a user mock-up should be made or not.
            :param user_is_admin: String that indicates whether or not the user is admin or not.
                Only valid values are '0' (no admin) and '1' (is admin). Any other values will raise an Exception.

            :returns: A dictionary with the following key-value pairs:
                -"random_person" : A random person of which the contents can be checked later on
                    -"path" : A url path that contains the id of the random person at the end (example: "/auth/531857")
        """
        path = '/auth/(.*)'
        self.set_up_custom_path([(path, main_application.AuthorizationStatusHandler)])
        self.testbed.init_user_stub()

        number_of_persons = random.randint(3, 10)
        random_person_index = random.randint(0, number_of_persons - 1)
        random_person = None

        random_person_index2 = 0
        while random_person_index2 == random_person_index:  # make sure we have a unique number
            random_person_index2 = random.randint(0, number_of_persons - 1)
        random_person2 = None
        for i in range(0, number_of_persons):
            person = PersonDataCreator.create_valid_person_data(i)
            if i == random_person_index:
                random_person = person
                #Now, initialize the person as a user in google's users API if the boolean param says so
                if user_is_logged_in:
                    self.testbed.setup_env(
                        overwrite=True,
                        USER_EMAIL=random_person.email,
                        USER_ID=str(random_person.key.integer_id()),
                        USER_IS_ADMIN=user_is_admin)
                path = "/auth/" + str(random_person.key.integer_id())
            elif i == random_person_index2:
                random_person2 = person

        return {"random_person": random_person, "path": path, "random_person2": random_person2}

    def test_get_user_status_positive_logged_in_no_admin(self):
        user_is_logged_in = True
        user_is_admin = '0'

        setup_data = self.setup_user_data(user_is_logged_in, user_is_admin)
        path = setup_data["path"]
        random_person = setup_data["random_person"]

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["id"])
            self.assertIsNotNone(response_data["is_logged_in"])
            self.assertIsNotNone(response_data["is_application_admin"])

            self.assertEqual(response_data["id"], str(random_person.key.integer_id()))
            self.assertEqual(response_data["is_logged_in"], user_is_logged_in)
            self.assertEqual(response_data["is_application_admin"], False)
        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "The values expected for each key are:\n"
                      "{\"id\" : integer,\n"
                      "\"is_logged_in\" : boolean,\n"
                      "\"is_application_admin\" : boolean}\n"
                      "______________________\n"
                      "Full error message:\n"
                      + str(error))

    def test_get_user_status_positive_not_logged_in_admin_unknown(self):
        user_is_logged_in = False
        user_is_admin = '1'  # have to set it to something, but doesn't matter since we won't know for sure

        setup_data = self.setup_user_data(user_is_logged_in, user_is_admin)
        path = setup_data["path"]
        random_person = setup_data["random_person"]

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["id"])
            self.assertIsNotNone(response_data["is_logged_in"])
            self.assertIsNotNone(response_data["is_application_admin"])

            self.assertEqual(response_data["id"], str(random_person.key.integer_id()))
            self.assertEqual(response_data["is_logged_in"], user_is_logged_in)
            self.assertEqual(response_data["is_application_admin"], "unknown")
        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "The values expected for each key are:\n"
                      "{\"id\" : integer,\n"
                      "\"is_logged_in\" : boolean,\n"
                      "\"is_application_admin\" : boolean}\n"
                      "______________________\n"
                      "Full error message:\n"
                      + str(error))

    def test_get_user_status_positive_logged_in_is_admin(self):
        user_is_logged_in = True
        user_is_admin = '1'

        setup_data = self.setup_user_data(user_is_logged_in, user_is_admin)
        path = setup_data["path"]
        random_person = setup_data["random_person"]

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["id"])
            self.assertIsNotNone(response_data["is_logged_in"])
            self.assertIsNotNone(response_data["is_application_admin"])

            self.assertEqual(response_data["id"], str(random_person.key.integer_id()))
            self.assertEqual(response_data["is_logged_in"], user_is_logged_in)
            self.assertEqual(response_data["is_application_admin"], True)
        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "The values expected for each key are:\n"
                      "{\"id\" : integer,\n"
                      "\"is_logged_in\" : boolean,\n"
                      "\"is_application_admin\" : boolean}\n"
                      "______________________\n"
                      "Full error message:\n"
                      + str(error))

    def test_get_user_status_negative_invalid_id_format(self):
        user_is_logged_in = False  # these don't matter since we expect an error response before the handler checks this
        user_is_admin = '1'

        self.setup_user_data(user_is_logged_in, user_is_admin)
        path = "/auth/some_string_key_which_is_invalid"  # create an invalid id format: a string instead of an integer

        self.negative_test_stub_handler(path, "get", 400)

    def test_get_user_status_negative_invalid_id_none_given(self):
        user_is_logged_in = False  # these don't matter since we expect an error response before the handler checks this
        user_is_admin = '1'

        self.setup_user_data(user_is_logged_in, user_is_admin)
        path = "/auth/"  # create an invalid id format: don't give an id at all

        self.negative_test_stub_handler(path, "get", 400)

    def test_get_user_status_negative_request_other_users_status(self):
        user_is_logged_in = True
        user_is_admin = '0'

        setup_data = self.setup_user_data(user_is_logged_in, user_is_admin)
        random_person2 = setup_data["random_person2"]
        path = "/auth/" + str(random_person2.key.integer_id())

        #We will try to make a request for person2's status whilst we are logged in as person (number one)
        self.negative_test_stub_handler(path, "get", 500)

    def test_get_user_status_negative_unknown_person(self):
        user_is_logged_in = True  # these don't matter since we expect an error response before the handler checks this
        user_is_admin = '0'

        self.setup_user_data(user_is_logged_in, user_is_admin)
        path = "/auth/" + str(9871 + random.randint(84, 711))  # create a path with an unknown integer id

        #We will try to make a request for person2's status whilst we are logged in as person (number one)
        self.negative_test_stub_handler(path, "get", 404)


class EmployeeDetailsHandlerTest(BaseTestClass):
    def test_get_employee_details(self):
        path = "/employees/details/(.*)"
        self.set_up_custom_path([(path, main_application.SpecificEmployeeDetailsHandler)])
        number_of_employees = random.randint(1, 10)
        test_person = PersonDataCreator.create_valid_employee_data(0)
        for i in range(0, number_of_employees):
            PersonDataCreator.create_valid_employee_data(i+1)

        path = "/employees/details/" + str(test_person.key.integer_id())

        self.positive_test_stub_handler(path, "get")

    def test_get_employee_details_invalid_id_format(self):
        path = "/employees/details/(.*)"
        self.set_up_custom_path([(path, main_application.SpecificEmployeeDetailsHandler)])

        number_of_employees = random.randint(1, 10)
        for i in range(0, number_of_employees):
            PersonDataCreator.create_valid_employee_data(i)

        path = "/employees/details/invalid_key_format"
        self.negative_test_stub_handler(path, "get", 500)

    def test_get_user_status_negative_invalid_id_none_given(self):
        path = "/employees/details/(.*)"
        self.set_up_custom_path([(path, main_application.SpecificEmployeeDetailsHandler)])

        number_of_employees = random.randint(1, 10)
        for i in range(0, number_of_employees):
            PersonDataCreator.create_valid_employee_data(i)

        path = "/employees/details/"

        self.negative_test_stub_handler(path, "get", 500)


class UserSettingsHandlerTest(BaseTestClass):
    def test_get_user_settings(self):
        path = "/user/settings/(.*)"
        self.set_up_custom_path([(path, main_application.UserSettingsHandler)])

        number_of_employees = random.randint(1, 10)
        test_person = PersonDataCreator.create_valid_employee_data(0)
        for i in range(0, number_of_employees):
            PersonDataCreator.create_valid_employee_data(i+1)

        path = '/user/settings/' + str(test_person.key.integer_id())
        self.positive_test_stub_handler(path, "get")
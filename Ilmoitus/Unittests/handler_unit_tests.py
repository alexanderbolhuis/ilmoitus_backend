__author__ = 'Sjors van Lemmen'
import random
import json
import ilmoitus_model
from google.appengine.ext import ndb
import ilmoitus as main_application
from test_data_creator import PersonDataCreator, DeclarationsDataCreator
from Base.base_test_methods import BaseTestClass


class EmployeeHandlerTest(BaseTestClass):
    def test_get_all_employee_positive(self):
        path = "/employees"
        self.set_up_test_server_with_custom_routes([(path, main_application.AllEmployeesHandler)])
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
        self.set_up_test_server_with_custom_routes([(path, main_application.AllEmployeesHandler)])
        number_of_persons = random.randint(1, 10)
        for i in range(0, number_of_persons):
            PersonDataCreator.create_valid_person_data(i)

        self.negative_test_stub_handler(path, "get", 404)

    def test_get_all_employee_negative_no_persons(self):
        """
         This test will test if the right error is given when there are no persons whatsoever.
        """
        path = "/employees"
        self.set_up_test_server_with_custom_routes([(path, main_application.AllEmployeesHandler)])

        self.negative_test_stub_handler(path, "get", 404)


class BaseAuthorizationHandler(BaseTestClass):
    def setup_server_with_user(self, handler_routes, user_is_logged_in, user_is_admin):
        """
            Helper method to set-up all data needed in these unit tests.

            :param handler_routes: List of tuples that contain all url and handlers that will be set-up for this test.
            :param user_is_logged_in: Boolean that indicates whether a user mock-up should be made or not.
            :param user_is_admin: String that indicates whether or not the user is admin or not.
                Only valid values are '0' (no admin) and '1' (is admin). Any other values will raise an Exception.

            :returns: A dictionary with the following key-value pairs:

                -"random_person" : A random person of which the contents can be checked later on

                -"path" : A url path that contains the id of the random person at the end (example: "/auth/531857")

                -"random_person2" : Another person object that will always be different from the first.
        """
        path = "/auth"
        self.set_up_test_server_with_custom_routes(handler_routes)
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
            elif i == random_person_index2:
                random_person2 = person

        return {"random_person": random_person, "path": path, "random_person2": random_person2}


class AuthorizationHandlerTest(BaseAuthorizationHandler):
    def test_get_user_status_positive_logged_in_no_admin(self):
        user_is_logged_in = True
        user_is_admin = '0'

        setup_data = self.setup_server_with_user([('/auth', main_application.AuthorizationStatusHandler)],
                                                 user_is_logged_in, user_is_admin)
        path = setup_data["path"]
        random_person = setup_data["random_person"]

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["person_id"])
            self.assertIsNotNone(response_data["is_logged_in"])
            self.assertIsNotNone(response_data["is_application_admin"])

            self.assertEqual(response_data["person_id"], random_person.key.integer_id())
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

        setup_data = self.setup_server_with_user([('/auth', main_application.AuthorizationStatusHandler)],
                                                 user_is_logged_in, user_is_admin)
        path = setup_data["path"]

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["is_logged_in"])

            self.assertEqual(response_data["is_logged_in"], user_is_logged_in)
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

        setup_data = self.setup_server_with_user([('/auth', main_application.AuthorizationStatusHandler)],
                                                 user_is_logged_in, user_is_admin)
        path = setup_data["path"]
        random_person = setup_data["random_person"]

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["person_id"])
            self.assertIsNotNone(response_data["is_logged_in"])
            self.assertIsNotNone(response_data["is_application_admin"])

            self.assertEqual(response_data["person_id"], (random_person.key.integer_id()))
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


class OpenDeclarationsForEmployeeHandlerTest(BaseAuthorizationHandler):
    def test_positive_get_all(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/open_declarations/employee'

        setup_data = self.setup_server_with_user(
            [('/open_declarations/employee', main_application.AllOpenDeclarationsForEmployeeHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        supervisor = PersonDataCreator.create_valid_supervisor()

        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()
        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)

        self.positive_test_stub_handler(path, "get")


class EmployeeDetailsHandlerTest(BaseAuthorizationHandler):
    def test_get_employee_details_not_logged_in(self):
        path = "/current_user_details/"
        self.set_up_test_server_with_custom_routes([(path, main_application.CurrentUserDetailsHandler)])

        self.negative_test_stub_handler(path, "get", 500)

    def test_get_employee_details_logged_in(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user_details/"
        self.setup_server_with_user([(path, main_application.CurrentUserDetailsHandler)],
                                    user_is_logged_in,
                                    user_is_admin)

        self.positive_test_stub_handler(path, "get")


class CurrentUserAssociatedDeclarationsTest(BaseAuthorizationHandler):
    def test_get_current_employee_associated_declarations(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/associated_declarations"
        setup_data = self.setup_server_with_user([(path, main_application.CurrentUserAssociatedDeclarations)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"
        logged_in_person._key = ndb.Key(model.User, logged_in_person.key.integer_id())
        logged_in_person.put()

        supervisor = PersonDataCreator.create_valid_supervisor()

        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)

        self.positive_test_stub_handler(path, "get")

    def test_get_current_employee_none_associated_declarations(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/associated_declarations"
        setup_data = self.setup_server_with_user([(path, main_application.CurrentUserAssociatedDeclarations)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"
        logged_in_person._key = ndb.Key(model.User, logged_in_person.key.integer_id())
        logged_in_person.put()

        supervisor = PersonDataCreator.create_valid_supervisor()

        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()

        self.negative_test_stub_handler(path, "get", 404)

    def test_get_current_supervisor_associated_declarations_assigned_to(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/associated_declarations"
        setup_data = self.setup_server_with_user([(path, main_application.CurrentUserAssociatedDeclarations)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "supervisor"
        logged_in_person._key = ndb.Key(model.User, logged_in_person.key.integer_id())
        logged_in_person.put()

        employee = PersonDataCreator.create_valid_employee_data()
        employee.supervisor = logged_in_person.key
        employee.put()
        DeclarationsDataCreator.create_valid_open_declaration(employee, logged_in_person)

        employee = PersonDataCreator.create_valid_employee_data()
        employee.supervisor = logged_in_person.key
        employee.put()
        DeclarationsDataCreator.create_valid_open_declaration(employee, logged_in_person)

        employee = PersonDataCreator.create_valid_employee_data()
        employee.supervisor = logged_in_person.key
        employee.put()
        DeclarationsDataCreator.create_valid_open_declaration(employee, logged_in_person)

        self.positive_test_stub_handler(path, "get")


class AllDeclarationsForHumanResourcesHandlerTest(BaseAuthorizationHandler):
    def test_positive_get_all(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/declarations/hr'

        setup_data = self.setup_server_with_user(
            [('/declarations/hr', main_application.AllDeclarationsForHumanResourcesHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "human_resources"
        logged_in_person.put()

        human_resource = PersonDataCreator.create_valid_human_resource()

        logged_in_person.human_resource = human_resource.key
        logged_in_person.put()
        valid_declaration = DeclarationsDataCreator.create_valid_approved_declaration(logged_in_person, human_resource)

        self.positive_test_stub_handler(path, "get")

    def test_negative_get_all_not_logged_in(self):
        path = '/declarations/hr'
        self.set_up_test_server_with_custom_routes([(path, main_application.AllDeclarationsForHumanResourcesHandler)])
        self.negative_test_stub_handler(path, "get", 401)

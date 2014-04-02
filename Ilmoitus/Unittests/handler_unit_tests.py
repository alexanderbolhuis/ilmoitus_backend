__author__ = 'Sjors van Lemmen'
import sys
sys.path.append("../")
import random
import json
import ilmoitus as main_application
from test_data_creator import PersonDataCreator, DeclarationsDataCreator
from Base.base_test_methods import BaseTestClass


class EmployeeHandlerTest(BaseTestClass):
    def test_get_all_employee_positive(self):
        path = "/employees"
        self.setup_test_server_with_custom_routes([(path, main_application.AllEmployeesHandler)])
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
        self.setup_test_server_with_custom_routes([(path, main_application.AllEmployeesHandler)])
        number_of_persons = random.randint(1, 10)
        for i in range(0, number_of_persons):
            PersonDataCreator.create_valid_person_data(i)

        self.negative_test_stub_handler(path, "get", 404)

    def test_get_all_employee_negative_no_persons(self):
        """
         This test will test if the right error is given when there are no persons whatsoever.
        """
        path = "/employees"
        self.setup_test_server_with_custom_routes([(path, main_application.AllEmployeesHandler)])

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
        self.setup_test_server_with_custom_routes(handler_routes)
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


class DeclarationsForEmployeeHandlerTest(BaseAuthorizationHandler):
    def test_positive_get_all(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/declarations/employee'

        setup_data = self.setup_server_with_user(
            [('/declarations/employee', main_application.AllDeclarationsForEmployeeHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()
        supervisor = PersonDataCreator.create_valid_supervisor()
        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        self.assertEqual(len(response_data), 1)

        try:
            self.assertIsNotNone(response_data[0]["id"])
            self.assertIsNotNone(response_data[0]["class_name"])
            self.assertIsNotNone(response_data[0]["state"])

            self.assertEqual(response_data[0]["created_by"], (logged_in_person.key.integer_id()))
            self.assertEqual(response_data[0]["assigned_to"][0], supervisor.key.integer_id())
        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "______________________\n"
                      "Full error message:\n"
                      + str(error))

    def test_negative_get_all_not_logged_in(self):
        path = '/declarations/employee'
        self.setup_test_server_with_custom_routes([(path, main_application.AllDeclarationsForEmployeeHandler)])
        self.negative_test_stub_handler(path, "get", 401)


class CurrentUserAssociatedDeclarationsTest(BaseAuthorizationHandler):  # TODO list fix
    def test_positive_get_current_employee_associated_declarations(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/associated_declarations"
        setup_data = self.setup_server_with_user([(path, main_application.CurrentUserAssociatedDeclarations)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        supervisor = PersonDataCreator.create_valid_supervisor()

        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)

        self.positive_test_stub_handler(path, "get")

    def test_negative_get_current_employee_none_associated_declarations(self):  # TODO list fix
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/associated_declarations"
        setup_data = self.setup_server_with_user([(path, main_application.CurrentUserAssociatedDeclarations)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        supervisor = PersonDataCreator.create_valid_supervisor()

        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()

        self.negative_test_stub_handler(path, "get", 404)

    def test_positive_get_current_supervisor_associated_declarations_assigned_to(self):  # TODO list fix
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/associated_declarations"
        setup_data = self.setup_server_with_user([(path, main_application.CurrentUserAssociatedDeclarations)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "supervisor"
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


class CurrentUserDetailHandlerTest(BaseAuthorizationHandler):
    def test_get_employee_details_logged_in(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/details"

        setup_data = self.setup_server_with_user(
            [(path, main_application.CurrentUserDetailsHandler)],
            user_is_logged_in, user_is_admin)

        random_person = setup_data["random_person"]

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["id"])
            self.assertIsNotNone(response_data["class_name"])
            self.assertIsNotNone(response_data["first_name"])
            self.assertIsNotNone(response_data["last_name"])
            self.assertIsNotNone(response_data["email"])

            self.assertEqual(response_data["id"], (random_person.key.integer_id()))
            self.assertEqual(response_data["class_name"], random_person.class_name)
            self.assertEqual(response_data["first_name"], random_person.first_name)
            self.assertEqual(response_data["last_name"], random_person.last_name)
            self.assertEqual(response_data["email"], random_person.email)
        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "The values expected for each key are:\n"
                      "{\"id\" : integer,\n"
                      "\"class_name\" : string,\n"
                      "\"first_name\" : string,\n"
                      "\"last_name\" : string,\n"
                      "\"email\" : string}\n"
                      "______________________\n"
                      "Full error message:\n"
                      + str(error))

    def test_get_employee_details_not_logged_in(self):
        path = "/current_user/details"
        self.setup_test_server_with_custom_routes([(path, main_application.CurrentUserDetailsHandler)])

        self.negative_test_stub_handler(path, "get", 401)


class AllDeclarationsForHumanResourcesHandlerTest(BaseAuthorizationHandler):

    def test_positive_get_all(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declarations/hr"

        setup_data = self.setup_server_with_user(
            [(path, main_application.AllDeclarationsForHumanResourcesHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "human_resources"

        logged_in_person.put()

        employee = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()

        DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declaration = DeclarationsDataCreator.create_valid_supervisor_approved_declaration(employee, supervisor)

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)
        print response_data

        self.assertEqual(response_data[0]["comment"], "Thanks for taking care of this for me!")
        self.assertEqual(response_data[0]["class_name"], "supervisor_approved_declaration")
        self.assertEqual(response_data[0]["created_at"], str(declaration.created_at))
        self.assertEqual(response_data[0]["created_by"], employee.key.integer_id())
        self.assertEqual(response_data[0]["approved_by"], supervisor.key.integer_id())
        self.assertEqual(response_data[0]["assigned_to"][0], supervisor.key.integer_id())
        self.assertEqual(response_data[0]["submitted_to_human_resources_by"], supervisor.key.integer_id())
        self.assertEqual(response_data[0]["id"], declaration.key.integer_id())

    def test_negative_get_all_not_logged_in(self):
        path = '/declarations/hr'

        self.setup_test_server_with_custom_routes([(path, main_application.AllDeclarationsForHumanResourcesHandler)])
        self.negative_test_stub_handler(path, "get", 401)


class CurrentUserSupervisorsHandlerTest(BaseAuthorizationHandler):
    def test_get_employee_supervisor_not_logged_in(self):
        path = "/supervisors/"

        self.setup_test_server_with_custom_routes([(path, main_application.CurrentUserSupervisors)])
        self.negative_test_stub_handler(path, "get", 401)

    def test_positive_get_all(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/supervisors/'

        setup_data = self.setup_server_with_user(
            [(path, main_application.CurrentUserSupervisors)],
            user_is_logged_in, user_is_admin)

        supervisor = PersonDataCreator.create_valid_supervisor()
        supervisor2 = PersonDataCreator.create_valid_supervisor()

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)
        print response_data

        for i in response_data:
            try:
                self.assertIsNotNone(i["class_name"])

                self.assertMultiLineEqual(i["class_name"], supervisor.class_name)
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


class AllDeclarationsForSupervisorTest(BaseAuthorizationHandler):
    def test_get_supervisor_declarations_no_permission(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declarations/supervisor"
        setup_data = self.setup_server_with_user([(path, main_application.AllDeclarationsForSupervisor)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"

        logged_in_person.put()

        self.negative_test_stub_handler(path, "get", 401)

    def test_get_supervisor_declarations(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declarations/supervisor"
        setup_data = self.setup_server_with_user([(path, main_application.AllDeclarationsForSupervisor)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "supervisor"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        other_supervisor = PersonDataCreator.create_valid_supervisor()

        DeclarationsDataCreator.create_valid_open_declaration(person, logged_in_person)
        DeclarationsDataCreator.create_valid_open_declaration(person, logged_in_person)
        DeclarationsDataCreator.create_valid_open_declaration(person, other_supervisor)

        response = self.positive_test_stub_handler(path, "get")
        response_data = json.loads(response.body)

        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]["assigned_to"][0], logged_in_person.key.integer_id())
        self.assertEqual(response_data[1]["assigned_to"][0], logged_in_person.key.integer_id())

class SetLockedToSupervisorDeclinedDeclarationHandlerTest(BaseAuthorizationHandler):
    def test_positive_put_one(self):
        user_is_logged_in = True
        user_is_admin = '1'
        path = "/decline_declaration/supervisor"
        self.setup_server_with_user([(path, main_application.SetLockedToSupervisorDeclinedDeclarationHandler)],
                                    user_is_logged_in,
                                    user_is_admin)
        employee = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()
        locked_declaration = DeclarationsDataCreator.create_valid_locked_declaration(employee, supervisor).get_object_json_data()

        #FIXME: fails because we need the new model; class name is absent from all_custom_properties
        response = self.positive_test_stub_handler(path, "put", data_dict=locked_declaration)
        self.assertTrue(isinstance(response, dict))
        self.assertTrue("id" in response.keys())
        self.assertEqual(locked_declaration["id"], response["id"])
        self.assertTrue("class_name" in response.keys())
        self.assertTrue(response["class_name"], "declined_declaration")

    def test_negative_put_none(self):
        user_is_logged_in = True
        user_is_admin = '1'
        path = "/decline_declaration/supervisor"
        self.setup_server_with_user([(path, main_application.SetLockedToSupervisorDeclinedDeclarationHandler)],
                                    user_is_logged_in,
                                    user_is_admin)
        locked_declaration_data = None
        self.negative_test_stub_handler(path, "put", 400, data_dict=locked_declaration_data)


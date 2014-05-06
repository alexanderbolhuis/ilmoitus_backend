__author__ = 'Sjors van Lemmen'
import sys

sys.path.append("../")
import random
import json
import ilmoitus_auth
import ilmoitus as main_application
import datetime
from test_data_creator import PersonDataCreator, DeclarationsDataCreator
from Base.base_test_methods import BaseTestClass
import ilmoitus_model


class EmployeeHandlerTest(BaseTestClass):
    def test_get_all_employee_positive(self):
        path = "/employees"
        self.setup_test_server_with_custom_routes([(path, main_application.AllEmployeesHandler)])
        number_of_employees = random.randint(1, 10)
        for i in range(0, number_of_employees):
            PersonDataCreator.create_valid_employee_data(i)

        self.positive_test_stub_handler("", path, "get")

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

        self.negative_test_stub_handler("", path, "get", 404)

    def test_get_all_employee_negative_no_persons(self):
        """
         This test will test if the right error is given when there are no persons whatsoever.
        """
        path = "/employees"
        self.setup_test_server_with_custom_routes([(path, main_application.AllEmployeesHandler)])

        self.negative_test_stub_handler("", path, "get", 404)


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
        token = None

        random_person_index2 = 0
        while random_person_index2 == random_person_index:  # make sure we have a unique number
            random_person_index2 = random.randint(0, number_of_persons - 1)
        random_person2 = None
        for i in range(0, number_of_persons):
            person = PersonDataCreator.create_valid_person_data(i)
            if i == random_person_index:
                random_person = person
                #Now, initialize the person as a user and generate token
                if user_is_logged_in:
                    result = ilmoitus_auth.authencate(random_person.email, "123456")
                    token = result["token"]

            elif i == random_person_index2:
                random_person2 = person

        return {"random_person": random_person, "token": token, "path": path, "random_person2": random_person2}


class AuthorizationHandlerTest(BaseAuthorizationHandler):
    def test_get_user_status_positive_logged_in_no_admin(self):
        user_is_logged_in = True
        user_is_admin = '0'

        setup_data = self.setup_server_with_user([('/auth', main_application.AuthorizationStatusHandler)],
                                                 user_is_logged_in, user_is_admin)

        #{"random_person": random_person, "token": token, "path": path, "random_person2": random_person2}



        path = setup_data["path"]
        random_person = setup_data["random_person"]
        token = setup_data["token"]

        response = self.positive_test_stub_handler(token, path, "get")
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
        token = setup_data["token"]

        response = self.positive_test_stub_handler(token, path, "get")
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
        token = setup_data["token"]

        response = self.positive_test_stub_handler(token, path, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["person_id"])
            self.assertIsNotNone(response_data["is_logged_in"])
            self.assertIsNotNone(response_data["is_application_admin"])

            self.assertEqual(response_data["person_id"], (random_person.key.integer_id()))
            self.assertEqual(response_data["is_logged_in"], user_is_logged_in)
            #self.assertEqual(response_data["is_application_admin"], True)
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
        token = setup_data["token"]

        supervisor = PersonDataCreator.create_valid_supervisor()
        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)

        response = self.positive_test_stub_handler(token, path, "get")
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
        self.negative_test_stub_handler("", path, "get", 401)


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
        token = setup_data["token"]

        supervisor = PersonDataCreator.create_valid_supervisor()

        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)
        DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)

        self.positive_test_stub_handler(token, path, "get")

    def test_negative_get_current_employee_none_associated_declarations(self):  # TODO list fix
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/associated_declarations"
        setup_data = self.setup_server_with_user([(path, main_application.CurrentUserAssociatedDeclarations)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()
        token = setup_data["token"]

        supervisor = PersonDataCreator.create_valid_supervisor()

        logged_in_person.supervisor = supervisor.key
        logged_in_person.put()

        self.negative_test_stub_handler(token, path, "get", 404)

    def test_positive_get_current_supervisor_associated_declarations_assigned_to(self):  # TODO list fix
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/associated_declarations"
        setup_data = self.setup_server_with_user([(path, main_application.CurrentUserAssociatedDeclarations)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "supervisor"
        logged_in_person.put()
        token = setup_data["token"]

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

        self.positive_test_stub_handler(token, path, "get")


class CurrentUserDetailHandlerTest(BaseAuthorizationHandler):
    def test_get_employee_details_logged_in(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/current_user/details"

        setup_data = self.setup_server_with_user(
            [(path, main_application.CurrentUserDetailsHandler)],
            user_is_logged_in, user_is_admin)

        random_person = setup_data["random_person"]
        token = setup_data["token"]

        response = self.positive_test_stub_handler(token, path, "get")
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

        self.negative_test_stub_handler("", path, "get", 401)


class SetLockedToSupervisorApprovedDeclarationHandlerTest(BaseAuthorizationHandler):
    def test_positive_put_one(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        supervisor = person
        employee = PersonDataCreator.create_valid_employee_data()
        locked_declaration = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor)
        supervisors_comment = "Ziet er goed uit maar let wel op item nummer 3!"
        #Add a comment as well
        locked_declaration.supervisor_comment = supervisors_comment
        locked_declaration.items_total_price = 150
        supervisor.max_declaration_price = -1
        locked_declaration.put()
        supervisor.put()
        locked_declaration_data = locked_declaration.get_object_as_data_dict()
        locked_declaration_data_json_string = json.dumps(locked_declaration_data)

        response = self.positive_test_stub_handler(token, path, "put", data_dict=locked_declaration_data_json_string)

        response_data = json.loads(response.body)

        self.assertTrue("id" in response_data.keys())
        self.assertEqual(locked_declaration_data["id"], response_data["id"])

        self.assertTrue("class_name" in response_data.keys())
        self.assertEqual(response_data["class_name"], "supervisor_approved_declaration")

        self.assertTrue("submitted_to_human_resources_by" in response_data.keys())
        self.assertEqual(response_data["submitted_to_human_resources_by"], supervisor.key.integer_id())

        self.assertTrue("supervisor_approved_at" in response_data.keys())
        # exact date-time is untestable: it's accurate in milliseconds.

        self.assertTrue("supervisor_comment" in response_data.keys())
        self.assertEqual(response_data["supervisor_comment"], supervisors_comment)

        messages = self.mail_stub.get_sent_messages()
        self.assertEqual(1, len(messages))

    def test_positive_put_two(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        supervisor = person
        employee = PersonDataCreator.create_valid_employee_data()
        locked_declaration = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor)
        supervisors_comment = "Ziet er goed uit maar let wel op item nummer 3!"
        #Add a comment as well
        locked_declaration.supervisor_comment = supervisors_comment
        locked_declaration.items_total_price = 150
        supervisor.max_declaration_price = 200
        locked_declaration.put()
        supervisor.put()
        locked_declaration_data = locked_declaration.get_object_as_data_dict()
        locked_declaration_data_json_string = json.dumps(locked_declaration_data)

        response = self.positive_test_stub_handler(token, path, "put", data_dict=locked_declaration_data_json_string)

        response_data = json.loads(response.body)

        self.assertTrue("id" in response_data.keys())
        self.assertEqual(locked_declaration_data["id"], response_data["id"])

        self.assertTrue("class_name" in response_data.keys())
        self.assertEqual(response_data["class_name"], "supervisor_approved_declaration")

        self.assertTrue("submitted_to_human_resources_by" in response_data.keys())
        self.assertEqual(response_data["submitted_to_human_resources_by"], supervisor.key.integer_id())

        self.assertTrue("supervisor_approved_at" in response_data.keys())
        # exact date-time is untestable: it's accurate in milliseconds.

        self.assertTrue("supervisor_comment" in response_data.keys())
        self.assertEqual(response_data["supervisor_comment"], supervisors_comment)

        messages = self.mail_stub.get_sent_messages()
        self.assertEqual(1, len(messages))

    def test_negative_put_one(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        supervisor = person
        employee = PersonDataCreator.create_valid_employee_data()
        locked_declaration = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor)
        supervisors_comment = "Ziet er goed uit maar let wel op item nummer 3!"
        #Add a comment as well
        locked_declaration.supervisor_comment = supervisors_comment
        locked_declaration.items_total_price = 150
        supervisor.max_declaration_price = 100
        locked_declaration.put()
        supervisor.put()
        locked_declaration_data = locked_declaration.get_object_as_data_dict()
        locked_declaration_data_json_string = json.dumps(locked_declaration_data)

        self.negative_test_stub_handler(token, path, "put", 401, data_dict=locked_declaration_data_json_string)


    def test_negative_put_none(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        locked_declaration_data = None

        self.negative_test_stub_handler(token, path, "put", 400, data_dict=locked_declaration_data)

    def test_negative_put_empty_dict(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        locked_declaration_data = {}

        self.negative_test_stub_handler(token, path, "put", 400, data_dict=json.dumps(locked_declaration_data))

    def test_negative_put_meaningless_string(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        locked_declaration_data = "Some string that will pass the None and length check, " \
                                  "but should fail on the valid json check"

        self.negative_test_stub_handler(token, path, "put", 400, data_dict=json.dumps(locked_declaration_data))

    def test_negative_put_invalid_id(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        supervisor = person
        employee = PersonDataCreator.create_valid_employee_data()

        locked_declaration_data = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor).get_object_as_data_dict()

        #Change the id to a string which is not a long (i.e. an invalid ID)
        locked_declaration_data["id"] = "some string that wont be a valid id"

        self.negative_test_stub_handler(token, path, "put", 400, data_dict=json.dumps(locked_declaration_data))

    def test_negative_put_id_not_found(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        supervisor = person
        employee = PersonDataCreator.create_valid_employee_data()

        locked_declaration_data = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor).get_object_as_data_dict()

        #Change the id to a long that does not exists in the datastore
        locked_declaration_data["id"] = long(578814894151775871)

        self.negative_test_stub_handler(token, path, "put", 404, data_dict=json.dumps(locked_declaration_data))

    def test_negative_put_no_id(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        supervisor = person
        employee = PersonDataCreator.create_valid_employee_data()

        locked_declaration_data = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor).get_object_as_data_dict()

        #Change the id to None
        locked_declaration_data["id"] = None

        self.negative_test_stub_handler(token, path, "put", 400, data_dict=json.dumps(locked_declaration_data))

    def test_negative_put_invalid_class_name(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        supervisor = person
        employee = PersonDataCreator.create_valid_employee_data()

        #Change the regular call to create_valid_locked_declaration to an open one:
        open_declaration_data = DeclarationsDataCreator.create_valid_open_declaration(
            employee,
            supervisor).get_object_as_data_dict()

        self.negative_test_stub_handler(token, path, "put", 422, data_dict=json.dumps(open_declaration_data))

    def test_negative_put_logged_in_user_is_not_assigned(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        token = setup_data["token"]
        person.put()

        supervisor = person
        employee = PersonDataCreator.create_valid_employee_data()

        locked_declaration = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor)

        #Change the assigned to to another supervisor
        locked_declaration.assigned_to = [PersonDataCreator.create_valid_supervisor().key]
        locked_declaration_data = locked_declaration.get_object_as_data_dict()

        self.negative_test_stub_handler(token, path, "put", 401, data_dict=json.dumps(locked_declaration_data))

    def test_negative_put_when_not_supervisor(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        #leave the person from the setup function so that it's not a supervisor

        supervisor = PersonDataCreator.create_valid_supervisor()
        employee = PersonDataCreator.create_valid_employee_data()

        locked_declaration_data = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor).get_object_as_data_dict()

        self.negative_test_stub_handler("", path, "put", 401, data_dict=json.dumps(locked_declaration_data))

    def test_negative_put_when_no_one_is_logged_in(self):
        user_is_logged_in = False
        user_is_admin = '0'
        path = "/approve_declaration/supervisor"
        setup_data = self.setup_server_with_user(
            [(path, main_application.SetLockedToSupervisorApprovedDeclarationHandler)],
            user_is_logged_in,
            user_is_admin)
        person = setup_data["random_person"]
        person.class_name = "supervisor"
        person.put()

        supervisor = PersonDataCreator.create_valid_supervisor()
        employee = PersonDataCreator.create_valid_employee_data()

        locked_declaration_data = DeclarationsDataCreator.create_valid_locked_declaration(
            employee,
            supervisor).get_object_as_data_dict()

        self.negative_test_stub_handler("", path, "put", 401, data_dict=json.dumps(locked_declaration_data))


class AllDeclarationsForHumanResourcesHandlerTest(BaseAuthorizationHandler):
    def test_positive_get_all(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declarations/hr"

        setup_data = self.setup_server_with_user(
            [(path, main_application.AllDeclarationsForHumanResourcesHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "human_resources"

        logged_in_person.put()

        employee = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()

        DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declaration = DeclarationsDataCreator.create_valid_supervisor_approved_declaration(employee, supervisor)

        response = self.positive_test_stub_handler(token, path, "get")
        response_data = json.loads(response.body)

        self.assertEqual(response_data[0]["comment"], "Thanks for taking care of this for me!")
        self.assertEqual(response_data[0]["class_name"], "supervisor_approved_declaration")
        self.assertEqual(response_data[0]["created_at"], str(declaration.created_at))
        self.assertEqual(response_data[0]["created_by"], employee.key.integer_id())

        self.assertEqual(response_data[0]["supervisor_approved_by"], supervisor.key.integer_id())
        self.assertEqual(response_data[0]["assigned_to"][0], supervisor.key.integer_id())
        self.assertEqual(response_data[0]["submitted_to_human_resources_by"], supervisor.key.integer_id())
        self.assertEqual(response_data[0]["id"], declaration.key.integer_id())

    def test_negative_get_all_not_logged_in(self):
        path = '/declarations/hr'

        self.setup_test_server_with_custom_routes([(path, main_application.AllDeclarationsForHumanResourcesHandler)])
        self.negative_test_stub_handler("", path, "get", 401)


class CurrentUserSupervisorsHandlerTest(BaseAuthorizationHandler):
    def test_get_employee_supervisor_not_logged_in(self):
        path = "/supervisors/"

        self.setup_test_server_with_custom_routes([(path, main_application.CurrentUserSupervisors)])
        self.negative_test_stub_handler("", path, "get", 401)

    def test_positive_get_all(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/supervisors/'

        setup_data = self.setup_server_with_user(
            [(path, main_application.CurrentUserSupervisors)],
            user_is_logged_in, user_is_admin)
        token = setup_data["token"]
        supervisor = PersonDataCreator.create_valid_supervisor()
        supervisor2 = PersonDataCreator.create_valid_supervisor()

        response = self.positive_test_stub_handler(token, path, "get")
        response_data = json.loads(response.body)

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
        token = setup_data["token"]
        logged_in_person.class_name = "employee"

        logged_in_person.put()

        self.negative_test_stub_handler(token, path, "get", 401)

    def test_get_supervisor_declarations(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declarations/supervisor"
        setup_data = self.setup_server_with_user([(path, main_application.AllDeclarationsForSupervisor)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "supervisor"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        other_supervisor = PersonDataCreator.create_valid_supervisor()

        DeclarationsDataCreator.create_valid_open_declaration(person, logged_in_person)
        DeclarationsDataCreator.create_valid_open_declaration(person, logged_in_person)
        DeclarationsDataCreator.create_valid_open_declaration(person, other_supervisor)

        response = self.positive_test_stub_handler(token, path, "get")
        response_data = json.loads(response.body)

        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]["assigned_to"][0], logged_in_person.key.integer_id())
        self.assertEqual(response_data[1]["assigned_to"][0], logged_in_person.key.integer_id())


class ApproveDeclarationByHumanResourcesTest(BaseAuthorizationHandler):
    def test_negative_approve_not_logged_in(self):
        user_is_logged_in = False
        user_is_admin = '0'
        path = "/declaration/approve_by_hr"
        self.setup_server_with_user([(path, main_application.ApproveByHumanResources)],
                                    user_is_logged_in, user_is_admin)

        self.negative_test_stub_handler("", path, "put", 401)

    def test_negative_approve_no_permission(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/approve_by_hr"
        setup_data = self.setup_server_with_user([(path, main_application.ApproveByHumanResources)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        self.negative_test_stub_handler(token, path, "put", 401)

    # TODO: Make put_json working
    def test_positive_approve(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/approve_by_hr"
        setup_data = self.setup_server_with_user([(path, main_application.ApproveByHumanResources)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "human_resources"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()

        declaration = DeclarationsDataCreator.create_valid_supervisor_approved_declaration(person, supervisor)


        #test approving a supervisor approved declaration
        post_data = json.dumps(dict(id=declaration.key.integer_id(), pay_date="2014-04-02T00:00:00.000Z"))
        response = self.positive_test_stub_handler(token, path, "put", data_dict=post_data)
        response_data = json.loads(response.body)
        self.assertEqual(response_data["class_name"], "human_resources_approved_declaration")
        self.assertEqual(response_data["human_resources_approved_by"], logged_in_person.key.integer_id())
        self.assertEqual(response_data["will_be_payed_out_on"], "2014-04-02")

        #seconds & minutes could easily change between insertion of the data and execution of this test.
        # Because of this, only check date and hour.
        self.assertEqual(declaration.human_resources_approved_at.strftime('%Y-%m-%d %H'),
                         datetime.datetime.now().strftime('%Y-%m-%d %H'))

        messages = self.mail_stub.get_sent_messages(to=ilmoitus_model.Person.get_by_id(response_data["created_by"]).email)
        self.assertEqual(1, len(messages))

    def test_negative_approve_open_declaration(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/approve_by_hr"
        setup_data = self.setup_server_with_user([(path, main_application.ApproveByHumanResources)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "human_resources"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(person, supervisor)

        #test approving an open declaration. (should not be possible)
        post_data = dict(id=declaration.key.integer_id(), pay_date="2014-04-02T00:00:00.000Z")
        self.negative_test_stub_handler(token, path, "put", 500, data_dict=post_data)


class SupervisorDeclarationToHrDeclinedDeclarationHandlerTest(BaseAuthorizationHandler):
    # TODO: Make put_json working
    def test_positive_decline(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/declaration/declined_by_hr'

        setup_data = self.setup_server_with_user(
            [(path, main_application.SupervisorDeclarationToHrDeclinedDeclarationHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "human_resources"
        logged_in_person.put()

        person_supervisor = PersonDataCreator.create_valid_supervisor()
        person_employee = PersonDataCreator.create_valid_employee_data()

        declaration_two = DeclarationsDataCreator.create_valid_supervisor_approved_declaration(person_employee, person_supervisor)

        data = json.dumps(dict(declaration_id=declaration_two.key.integer_id()))
        response = self.positive_test_stub_handler(token, path, 'put', data_dict=data)
        response_data = json.loads(response.body)
        self.assertEqual(response_data["class_name"], 'human_resources_declined_declaration')
        self.assertEqual(response_data["human_resources_declined_by"], logged_in_person.key.integer_id())
        self.assertEqual(response_data["human_resources_declined_by"], logged_in_person.key.integer_id())
        self.assertNotEqual(response_data["human_resources_declined_at"], None)

        messages = self.mail_stub.get_sent_messages()
        self.assertEqual(1, len(messages))

    def test_negative_decline_open_declaration_by_human_resources(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/declaration/declined_by_hr'

        setup_data = self.setup_server_with_user(
            [(path, main_application.SupervisorDeclarationToHrDeclinedDeclarationHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "human_resources"
        logged_in_person.put()

        person_supervisor = PersonDataCreator.create_valid_supervisor()
        person_employee = PersonDataCreator.create_valid_employee_data()

        declaration = DeclarationsDataCreator.create_valid_open_declaration(person_employee, person_supervisor)

        data_one = json.dumps(dict(declaration_id=declaration.key.integer_id()))

        self.negative_test_stub_handler(token, path, 'put', 500, data_one)

    def test_negative_put_is_none(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/declaration/declined_by_hr'

        setup_data = self.setup_server_with_user(
            [(path, main_application.SupervisorDeclarationToHrDeclinedDeclarationHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "human_resources"
        logged_in_person.put()

        self.negative_test_stub_handler(token, path, 'put', 500, data_dict=None)

    def test_negative_decline_no_permission(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = '/declaration/declined_by_hr'

        setup_data = self.setup_server_with_user(
            [(path, main_application.SupervisorDeclarationToHrDeclinedDeclarationHandler)],
            user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        self.negative_test_stub_handler(token, path, "put", 401)

    def test_negative_decline_not_logged_in(self):
        # TODO: Incomplete code!
        user_is_logged_in = False
        user_is_admin = '0'
        path = '/declaration/declined_by_hr'

        self.setup_server_with_user(
            [(path, main_application.SupervisorDeclarationToHrDeclinedDeclarationHandler)],
            user_is_logged_in, user_is_admin)


class SpecificDeclarationTest(BaseAuthorizationHandler):
    def test_positive_get_employee_declaration(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/(.*)"

        setup_data = self.setup_server_with_user(
            [(path, main_application.SpecificDeclarationHandler)],
            user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"

        logged_in_person.put()

        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration_valid = DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)

        path = "/declaration/" + str(declaration_valid.key.integer_id())
        response = self.positive_test_stub_handler(token, path, "get")
        response_data = json.loads(response.body)

        # check for VALID declaration by logged_in_person
        self.assertEqual(response_data["created_by"], logged_in_person.key.integer_id())
        self.assertEqual(response_data["id"], declaration_valid.key.integer_id())

    def test_positive_get_supervisor_declaration(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/(.*)"
        setup_data = self.setup_server_with_user([(path, main_application.SpecificDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "supervisor"

        logged_in_person.put()

        employee = PersonDataCreator.create_valid_employee_data()

        # check if supervisor can open an open declaration
        declaration_open = DeclarationsDataCreator.create_valid_open_declaration(employee, logged_in_person)
        path1 = "/declaration/" + str(declaration_open.key.integer_id())

        response1 = self.positive_test_stub_handler(token, path1, "get")
        response_data1 = json.loads(response1.body)

        # check for VALID declaration by logged_in_person
        self.assertEquals(response_data1["assigned_to"][0], logged_in_person.key.integer_id())
        self.assertEquals(response_data1["id"], declaration_open.key.integer_id())
        self.assertEquals(response_data1["class_name"], "open_declaration")

         # check if supervisor can open an locked declaration
        declaration_lock = DeclarationsDataCreator.create_valid_locked_declaration(employee, logged_in_person)
        path2 = "/declaration/" + str(declaration_lock.key.integer_id())

        response2 = self.positive_test_stub_handler(token, path2, "get")
        response_data2 = json.loads(response2.body)

        # check for VALID declaration by logged_in_person
        self.assertEquals(response_data2["assigned_to"][0], logged_in_person.key.integer_id())
        self.assertEquals(response_data2["id"], declaration_lock.key.integer_id())
        self.assertEquals(response_data2["class_name"], "locked_declaration")

    def test_positive_get_hr_declaration(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/(.*)"
        setup_data = self.setup_server_with_user([(path, main_application.SpecificDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "human_resources"
        logged_in_person.put()

        employee = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()

        declaration_valid = DeclarationsDataCreator.create_valid_supervisor_approved_declaration(employee, supervisor)

        path = "/declaration/" + str(declaration_valid.key.integer_id())

        response = self.positive_test_stub_handler(token, path, "get")
        response_data = json.loads(response.body)

        # check for VALID declaration by logged_in_person
        self.assertEquals(response_data["submitted_to_human_resources_by"], supervisor.key.integer_id())
        self.assertEquals(response_data["id"], declaration_valid.key.integer_id())
        self.assertEquals(response_data["class_name"], "supervisor_approved_declaration")

    def test_negative_get_employee_declaration_by_other_employee(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/(.*)"

        setup_data = self.setup_server_with_user(
            [(path, main_application.SpecificDeclarationHandler)],
            user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"

        logged_in_person.put()

        employee = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()

        # checks if other login employee can get the declaration
        declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        path = "/declaration/" + str(declaration.key.integer_id())
        self.negative_test_stub_handler(token, path, "get", 401)

    def test_negative_get_supervisor_declaration_not_assigned_to_login_supervisor(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/(.*)"
        setup_data = self.setup_server_with_user([(path, main_application.SpecificDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "supervisor"

        logged_in_person.put()

        employee = PersonDataCreator.create_valid_employee_data()
        other_supervisor = PersonDataCreator.create_valid_supervisor()

        # checks if supervisor can see an declaration assigned to an other supervisor
        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, other_supervisor)
        path = "/declaration/" + str(open_declaration.key.integer_id())
        self.negative_test_stub_handler(token, path, "get", 401)

        # checks if an supervisor can see an declaration assigned to an other supervisor
        open_declaration = \
            DeclarationsDataCreator.create_valid_open_declaration(employee, other_supervisor)
        path = "/declaration/" + str(open_declaration.key.integer_id())
        self.negative_test_stub_handler(token, path, "get", 401)

    def test_negative_get_hr_declaration_open_declaration(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/(.*)"
        setup_data = self.setup_server_with_user([(path, main_application.SpecificDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "human_resources"
        logged_in_person.put()

        employee = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()

        # checks if hr can see an open declaration
        open_declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        path = "/declaration/" + str(open_declaration.key.integer_id())
        self.negative_test_stub_handler(token, path, "get", 401)

    def test_negative_declaration_not_found(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/(.*)"

        setup_data = self.setup_server_with_user(
            [(path, main_application.SpecificDeclarationHandler)],
            user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"

        logged_in_person.put()

        supervisor = PersonDataCreator.create_valid_supervisor()

        declaration = DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)
        declaration_id = declaration.key.integer_id()
        declaration.key.delete()

        path = "/declaration/" + str(declaration_id)

        self.negative_test_stub_handler(token, path, "get", 404)

    def test_negative_declaration_sent_text_as_id(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/(.*)"

        setup_data = self.setup_server_with_user(
            [(path, main_application.SpecificDeclarationHandler)],
            user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"

        logged_in_person.put()

        path = "/declaration/test"

        self.negative_test_stub_handler(token, path, "get", 400)

    def test_negative_declaration_no_user_logging(self):
        user_is_logged_in = False
        user_is_admin = '0'
        path = "/declaration/(.*)"

        setup_data = self.setup_server_with_user(
            [(path, main_application.SpecificDeclarationHandler)],
            user_is_logged_in, user_is_admin)
        token = setup_data["token"]

        logged_in_person = setup_data["random_person"]
        logged_in_person.class_name = "employee"

        logged_in_person.put()

        path = "/declaration/test"

        self.negative_test_stub_handler(token, path, "get", 401)


class GetAttachmentTest(BaseAuthorizationHandler):
    def test_get_attachment_positive(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/attachment/(.*)"

        setup_data = self.setup_server_with_user([(path, main_application.SpecificAttachmentHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()
        supervisor = PersonDataCreator.create_valid_supervisor()

        declaration = DeclarationsDataCreator.create_valid_open_declaration(logged_in_person, supervisor)
        attachments = DeclarationsDataCreator.create_valid_declaration_attachments(declaration, 2)

        path = "/attachment/"+str(attachments[0].key.integer_id())
        response = self.positive_test_stub_handler(token, path, "get")

        response_data = json.loads(response.body)
        self.assertEqual(response_data["id"], attachments[0].key.integer_id())
        self.assertEqual(response_data["declaration"], declaration.key.integer_id())
        self.assertEqual(response_data["file"], attachments[0].file)


class AddNewDeclarationHandlerTest(BaseAuthorizationHandler):
    def test_add_new_declaration_one_item_positive(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration"

        setup_data = self.setup_server_with_user([(path, main_application.AddNewDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        employee = logged_in_person
        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declarationlines = DeclarationsDataCreator.create_valid_declaration_lines(declaration, 1)
        declarationattachments = DeclarationsDataCreator.create_valid_declaration_attachments(declaration, 2)

        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), declarationlines)
        attachments = map(lambda declaration_attachment: declaration_attachment.get_object_as_data_dict(), declarationattachments)

        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines,
                                    'attachments': attachments})

        for declarationline in declarationlines:
            declarationline.key.delete()

        for declarationattachment in declarationattachments:
            declarationattachment.key.delete()

        declaration.key.delete()

        items_total_price = lines[0]["cost"]
        response = self.positive_test_stub_handler(token, path, "post", data_dict=combined_dict)

        response_data = json.loads(response.body)

        response_declaration = response_data["declaration"]
        response_declarationlines = response_data["lines"]
        response_attachments = response_data["attachments"]

        try:
            self.assertIsNotNone(response_declaration["id"])
            self.assertIsNotNone(response_declaration["created_by"])
            self.assertIsNotNone(response_declaration["assigned_to"])
            self.assertEqual(response_declaration["items_count"], "1")
            self.assertEqual(response_declaration["items_total_price"], items_total_price)
            self.assertIsNotNone(response_declarationlines[0]["declaration"])
            self.assertIsNotNone(response_declarationlines[0]["declaration_sub_type"])
            self.assertEqual(response_attachments[0]["name"], declarationattachments[0].name)
            self.assertEqual(response_attachments[0]["file"], declarationattachments[0].file)
            self.assertEqual(response_attachments[1]["name"], declarationattachments[1].name)
            self.assertEqual(response_attachments[1]["file"], declarationattachments[1].file)

            self.assertEqual(response_declaration["created_by"], (employee.key.integer_id()))
            self.assertEqual(response_declaration["assigned_to"], [supervisor.key.integer_id()])
            self.assertEqual(response_declarationlines[0]["declaration"], response_declaration["id"])

        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "The values expected for each key are:\n"
                      "{\"id\" : integer,\n"
                      "\"created_by\" : integer,\n"
                      "\"assigned_to\" : integer,\n"
                      "\"declaration\" : integer,\n"
                      "\"declaration_sub_type\" : integer}\n"
                      "______________________\n"
                      "Full error message:\n"
                      + str(error))

    def test_add_new_declaration_more_items_positive(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration"

        setup_data = self.setup_server_with_user([(path, main_application.AddNewDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        employee = logged_in_person
        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declarationlines = DeclarationsDataCreator.create_valid_declaration_lines(declaration, 3)
        declarationattachments = DeclarationsDataCreator.create_valid_declaration_attachments(declaration, 2)

        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), declarationlines)
        attachments = map(lambda declaration_attachment: declaration_attachment.get_object_as_data_dict(), declarationattachments)

        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines,
                                    'attachments': attachments})

        for declarationline in declarationlines:
            declarationline.key.delete()

        for declarationattachment in declarationattachments:
            declarationattachment.key.delete()

        declaration.key.delete()

        items_total_price = 0
        for line in lines:
            items_total_price += int(line["cost"])

        response = self.positive_test_stub_handler(token, path,
                                                   "post",
                                                   data_dict=combined_dict)

        response_data = json.loads(response.body)
        response_declaration = response_data["declaration"]
        response_declarationlines = response_data["lines"]
        response_attachments = response_data["attachments"]

        try:
            self.assertIsNotNone(response_declaration["id"])
            self.assertIsNotNone(response_declaration["created_by"])
            self.assertIsNotNone(response_declaration["assigned_to"])
            self.assertEqual(response_declaration["items_count"], "3")
            self.assertEqual(response_declaration["items_total_price"], str(items_total_price))
            self.assertIsNotNone(response_declarationlines[0]["declaration"])
            self.assertIsNotNone(response_declarationlines[0]["declaration_sub_type"])
            self.assertIsNotNone(response_declarationlines[1]["declaration"])
            self.assertIsNotNone(response_declarationlines[1]["declaration_sub_type"])
            self.assertIsNotNone(response_declarationlines[2]["declaration"])
            self.assertIsNotNone(response_declarationlines[2]["declaration_sub_type"])
            self.assertEqual(response_attachments[0]["name"], declarationattachments[0].name)
            self.assertEqual(response_attachments[0]["file"], declarationattachments[0].file)
            self.assertEqual(response_attachments[1]["name"], declarationattachments[1].name)
            self.assertEqual(response_attachments[1]["file"], declarationattachments[1].file)

            self.assertEqual(response_declaration["created_by"], (employee.key.integer_id()))
            self.assertEqual(response_declaration["assigned_to"], [supervisor.key.integer_id()])
            self.assertEqual(response_declarationlines[0]["declaration"], response_declaration["id"])
            self.assertEqual(response_declarationlines[1]["declaration"], response_declaration["id"])
            self.assertEqual(response_declarationlines[2]["declaration"], response_declaration["id"])

        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "The values expected for each key are:\n"
                      "{\"id\" : integer,\n"
                      "\"created_by\" : integer,\n"
                      "\"assigned_to\" : integer,\n"
                      "\"declaration\" : integer,\n"
                      "\"declaration_sub_type\" : integer}\n"
                      "______________________\n"
                      "Full error message:\n"
                      + str(error))

    def test_add_new_declartion_postive_no_attachments(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration"

        setup_data = self.setup_server_with_user([(path, main_application.AddNewDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        employee = logged_in_person
        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declarationlines = DeclarationsDataCreator.create_valid_declaration_lines(declaration, 1)

        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), declarationlines)
        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines})

        for declarationline in declarationlines:
            declarationline.key.delete()

        declaration.key.delete()

        items_total_price = lines[0]["cost"]

        response = self.positive_test_stub_handler(token, path, "post", data_dict=combined_dict)

        response_data = json.loads(response.body)

        response_declaration = response_data["declaration"]
        response_declarationlines = response_data["lines"]
        response_attachments = response_data["attachments"]

        try:
            self.assertIsNotNone(response_declaration["id"])
            self.assertIsNotNone(response_declaration["created_by"])
            self.assertIsNotNone(response_declaration["assigned_to"])
            self.assertEqual(response_declaration["items_count"], "1")
            self.assertEqual(response_declaration["items_total_price"], items_total_price)
            self.assertIsNotNone(response_declarationlines[0]["declaration"])
            self.assertIsNotNone(response_declarationlines[0]["declaration_sub_type"])

            self.assertEqual(response_declaration["created_by"], (employee.key.integer_id()))
            self.assertEqual(response_declaration["assigned_to"], [supervisor.key.integer_id()])
            self.assertEqual(response_declarationlines[0]["declaration"], response_declaration["id"])

        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "The values expected for each key are:\n"
                      "{\"id\" : integer,\n"
                      "\"created_by\" : integer,\n"
                      "\"assigned_to\" : integer,\n"
                      "\"declaration\" : integer,\n"
                      "\"declaration_sub_type\" : integer}\n"
                      "______________________\n"
                      "Full error message:\n"
                      + str(error))

    def test_add_new_declaration_negative(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration"

        setup_data = self.setup_server_with_user([(path, main_application.AddNewDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        employee = logged_in_person
        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declarationlines = DeclarationsDataCreator.create_valid_declaration_lines(declaration, 1)
        declarationattachments = DeclarationsDataCreator.create_valid_declaration_attachments(declaration, 2)

        declaration.assigned_to[0] = None

        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), declarationlines)
        attachments = map(lambda declaration_attachment: declaration_attachment.get_object_as_data_dict(), declarationattachments)

        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines,
                                    'attachments': attachments})

        for declarationline in declarationlines:
            declarationline.key.delete()

        for declarationattachment in declarationattachments:
            declarationattachment.key.delete()

        declaration.key.delete()

        self.negative_test_stub_handler(token, path, "post", 400, combined_dict)

    def test_add_new_declaration_one_line_negative(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration"

        setup_data = self.setup_server_with_user([(path, main_application.AddNewDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        employee = logged_in_person
        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declarationlines = DeclarationsDataCreator.create_valid_declaration_lines(declaration, 1)
        declarationattachments = DeclarationsDataCreator.create_valid_declaration_attachments(declaration, 2)

        for declarationline in declarationlines:
            declarationline.declaration_sub_type = None

        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), declarationlines)
        attachments = map(lambda declaration_attachment: declaration_attachment.get_object_as_data_dict(), declarationattachments)

        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines,
                                    'attachments': attachments})

        for declarationline in declarationlines:
            declarationline.key.delete()

        for declarationattachment in declarationattachments:
            declarationattachment.key.delete()

        declaration.key.delete()

        self.negative_test_stub_handler(token, path, "post", 400, combined_dict)

    def test_add_new_declaration_more_lines_negative(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration"

        setup_data = self.setup_server_with_user([(path, main_application.AddNewDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        employee = logged_in_person
        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declarationlines = DeclarationsDataCreator.create_valid_declaration_lines(declaration, 3)
        declarationattachments = DeclarationsDataCreator.create_valid_declaration_attachments(declaration, 2)

        for declarationline in declarationlines:
            declarationline.declaration_sub_type = None

        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), declarationlines)
        attachments = map(lambda declaration_attachment: declaration_attachment.get_object_as_data_dict(), declarationattachments)

        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines,
                                    'attachments': attachments})

        for declarationline in declarationlines:
            declarationline.key.delete()

        for declarationattachment in declarationattachments:
            declarationattachment.key.delete()

        declaration.key.delete()

        self.negative_test_stub_handler(token, path, "post", 400, combined_dict)

    def test_add_new_declaration_negative_wrong_attachment(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration"

        setup_data = self.setup_server_with_user([(path, main_application.AddNewDeclarationHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        employee = logged_in_person
        supervisor = PersonDataCreator.create_valid_supervisor()
        declaration = DeclarationsDataCreator.create_valid_open_declaration(employee, supervisor)
        declarationlines = DeclarationsDataCreator.create_valid_declaration_lines(declaration, 1)
        declarationattachments = DeclarationsDataCreator.create_valid_declaration_attachments(declaration, 2)

        declarationattachments[1].file = declarationattachments[1].file.replace("application/pdf", "application/x-msdownload")

        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), declarationlines)
        attachments = map(lambda declaration_attachment: declaration_attachment.get_object_as_data_dict(), declarationattachments)

        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines,
                                    'attachments': attachments})

        for declarationline in declarationlines:
            declarationline.key.delete()

        for declarationattachment in declarationattachments:
            declarationattachment.key.delete()

        declaration.key.delete()
        self.negative_test_stub_handler(token, path, "post", 400, combined_dict)


# TODO: Make put_json working
class SetOpenToLockedDeclarationTest(BaseAuthorizationHandler):
    def test_negative_not_logged_in(self):
        user_is_logged_in = False
        user_is_admin = '0'
        path = "/declaration/lock"
        self.setup_server_with_user([(path, main_application.SetOpenToLockedDeclaration)],
                                    user_is_logged_in, user_is_admin)

        #self.negative_test_stub_handler("", path, "put_json", 401)

    def test_negative_no_permission(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/lock"
        setup_data = self.setup_server_with_user([(path, main_application.SetOpenToLockedDeclaration)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "employee"
        logged_in_person.put()

        #self.negative_test_stub_handler(token, path, "put_json", 401)

    def test_positive(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/lock"
        setup_data = self.setup_server_with_user([(path, main_application.SetOpenToLockedDeclaration)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "supervisor"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()

        declaration1 = DeclarationsDataCreator.create_valid_open_declaration(person, supervisor)
        declaration2 = DeclarationsDataCreator.create_valid_supervisor_approved_declaration(person, supervisor)
        declaration3 = DeclarationsDataCreator.create_valid_open_declaration(person, supervisor)

        ''''
        #test locking a declaration
        post_data = dict(id=declaration1.key.integer_id())
        self.positive_test_stub_handler(token, path, "put_json", data_dict=post_data)
        self.assertEqual(declaration1.class_name, "locked_declaration")
        #seconds & minutes could easily change between insertion of the data and execution of this test.
        # Because of this, only check date and hour.
        self.assertEqual(declaration1.locked_at.strftime('%Y-%m-%d %H'),
                         datetime.datetime.now().strftime('%Y-%m-%d %H'))
        self.assertEqual(declaration2.class_name, "supervisor_approved_declaration")
        self.assertEqual(declaration3.class_name, "open_declaration")
        '''

    def test_negative_not_open(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/declaration/lock"
        setup_data = self.setup_server_with_user([(path, main_application.SetOpenToLockedDeclaration)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "supervisor"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        supervisor = PersonDataCreator.create_valid_supervisor()

        declaration1 = DeclarationsDataCreator.create_valid_open_declaration(person, supervisor)
        declaration2 = DeclarationsDataCreator.create_valid_supervisor_approved_declaration(person, supervisor)
        declaration3 = DeclarationsDataCreator.create_valid_open_declaration(person, supervisor)

        #test approving an other declaration. (should not be possible)
        #post_data = dict(id=declaration2.key.integer_id())
        #self.negative_test_stub_handler(token, path, "put_json", 500, data_dict=post_data)
        #self.assertEqual(declaration1.class_name, "open_declaration")
        #self.assertEqual(declaration2.class_name, "supervisor_approved_declaration")
        #self.assertEqual(declaration3.class_name, "open_declaration")


class DeclarationCountAndTotalAmountTest(BaseAuthorizationHandler):
    def test_one_declaration_positive(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/employees/total_declarations/(.*)"

        setup_data = self.setup_server_with_user([(path, main_application.SpecificEmployeeTotalDeclarationsHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "Supervisor"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        person.supervisor = logged_in_person.key
        person.put()

        valid_approved_declaration = DeclarationsDataCreator.create_valid_human_resources_approved_declaration(person, logged_in_person)
        valid_approved_declaration.items_total_price = 500
        valid_approved_declaration.put()

        getpath = "/employees/total_declarations/" + str(person.key.integer_id())
        response = self.positive_test_stub_handler(token, getpath, "get")
        response_data = json.loads(response.body)

        try:
            self.assertIsNotNone(response_data["open_declarations"])
            self.assertIsNotNone(response_data["accepted_declarations"])
            self.assertIsNotNone(response_data["denied_declarations"])
            self.assertIsNotNone(response_data["total_declarated_price"])

            self.assertEqual(response_data["total_declarated_price"], valid_approved_declaration.items_total_price)
            self.assertEqual(response_data["accepted_declarations"], 1)
            self.assertEqual(response_data["open_declarations"], 0)
            self.assertEqual(response_data["denied_declarations"], 0)
        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "Full error message:\n"
                      + str(error))

    def test_more_declarations_positive(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/employees/total_declarations/(.*)"

        setup_data = self.setup_server_with_user([(path, main_application.SpecificEmployeeTotalDeclarationsHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "Supervisor"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        person.supervisor = logged_in_person.key
        person.put()

        valid_approved_declaration1 = DeclarationsDataCreator.create_valid_human_resources_approved_declaration(person, logged_in_person)
        valid_approved_declaration1.items_total_price = 500
        valid_approved_declaration1.put()
        valid_approved_declaration2 = DeclarationsDataCreator.create_valid_human_resources_approved_declaration(person, logged_in_person)
        valid_approved_declaration2.items_total_price = 250
        valid_approved_declaration2.put()

        getpath = "/employees/total_declarations/" + str(person.key.integer_id())
        response = self.positive_test_stub_handler(token, getpath, "get")
        response_data = json.loads(response.body)

        try:
            total_cost = valid_approved_declaration1.items_total_price + valid_approved_declaration2.items_total_price

            self.assertIsNotNone(response_data["open_declarations"])
            self.assertIsNotNone(response_data["accepted_declarations"])
            self.assertIsNotNone(response_data["denied_declarations"])
            self.assertIsNotNone(response_data["total_declarated_price"])

            self.assertEqual(response_data["total_declarated_price"], total_cost)
            self.assertEqual(response_data["accepted_declarations"], 2)
            self.assertEqual(response_data["open_declarations"], 0)
            self.assertEqual(response_data["denied_declarations"], 0)
        except KeyError as error:
            self.fail("Test Failed! Expected the key: " + str(
                error) + " to be present in the response, but it was not found. Found only: " + str(response_data))
        except ValueError as error:
            self.fail("Test Failed! There is an invalid value in the response data. "
                      "This usually happens with parsing wrong input values.\n"
                      "Full error message:\n"
                      + str(error))

    def test_negative_get_id_not_found(self):
        user_is_logged_in = True
        user_is_admin = '0'
        path = "/employees/total_declarations/(.*)"

        setup_data = self.setup_server_with_user([(path, main_application.SpecificEmployeeTotalDeclarationsHandler)],
                                                 user_is_logged_in, user_is_admin)

        logged_in_person = setup_data["random_person"]
        token = setup_data["token"]
        logged_in_person.class_name = "Supervisor"
        logged_in_person.put()

        person = PersonDataCreator.create_valid_employee_data()
        person.supervisor = logged_in_person.key
        person.put()

        getpath = "/employees/total_declarations/" + str(99999)
        self.negative_test_stub_handler(token, getpath, "get", 404)

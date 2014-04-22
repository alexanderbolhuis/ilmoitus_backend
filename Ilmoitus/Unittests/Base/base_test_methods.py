__author__ = 'Sjors van Lemmen'
from unittest import TestCase
import webapp2
import json
import webtest
from google.appengine.ext import testbed
from google.appengine.api import apiproxy_stub_map

import ilmoitus as main_application


class BaseTestClass(TestCase):
    """
    This class contains the basic methods that (for instance) will set-up a basic
    test-bed, or a customizable test-bed that will initialize with pre-determined
    handlers and routes. It also holds several generic testing methods that will
    not only allow unit tests to easily test on multiple conditions in a read-able
    fashion, but they also reduce code bloating by a significant margin.
    """

    def setup_test_server_with_custom_routes(self, handler_routes=([(None, None)])):
        """
        This method sets up a testbed object using the given handlers and paths.
        This allows tests to specify specific paths to be used for the given handler.

        This method overrides the function that is called by default by webtest
        whenever a unittest is called (so not calling THIS method will result
        in the default implementation of webtest being called). The default
        implementation is an empty function, so that should never be used!

        :param handler_routes:
            A list containing tuples of all (unique) urls that and their handler.
            If it's None, no urls and no handlers will be set for the test application.
        """
        # Create a WSGI application.
        dummy_app = webapp2.WSGIApplication(handler_routes)

        # Wrap the app with WebTests TestApp and activate it with a datastore stub.
        self.testapp = webtest.TestApp(dummy_app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def setup_test_server_without_handlers(self):
        """
         As the name implies, this method creates a server in exactly the same fashion
         as the set_up_test_server_with_custom_routes function, but without any handlers
         attached to the server.

         This can be useful if there is a test that needs to put model objects, but doesn't
         need any handlers.
        """
        # Create a WSGI application.
        dummy_app = webapp2.WSGIApplication(
            [(None, None)])  # shouldn't matter since we won't be sending requests

        # Wrap the app with WebTests TestApp and activate it with a datastore stub.
        self.testapp = webtest.TestApp(dummy_app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        """
        This method overrides the default implantation of Webtest's tearDown method.
        This method simply deactivates the testbed application and is called
        automatically whenever a unittest class is finished with it's tests.
        """
        try:
            self.testbed.deactivate()
        except AttributeError:
            #If there was no testbed to begin with, return without doing anything
            return

    def positive_test_stub_for_model_data_validity(self, data_object, header_string=None):
        """
        This method is used by all model tests that test on data validity for model objects.
        Here, the default check_data_validity method that every model class implements will
        be called and it's results saved. If there are any errors, the test fails after
        printing all the error messages (through the error's msg field) that occurred.

        If there are no errors, a short "success" message will be printed on the console.

        Additionally, a header string can be passed that should be printed. This can contain
        a simple indication of what is tested (which class) which will improve read-ability
        of test results.

        :param data_object:
            The object that needs to be tested for data validity. Must belong to a class
            that implements the check_data_validity method and all errors that this method
            produce must have a msg field implemented that contains a description of what
            the error is.
        :param header_string:
            (Optional) A string that should be printed before anything else, that can display
             what (type of object) will be tested. Used to improve read-ability of test results.
        """
        if header_string is not None:
            print header_string
        invalid_data_error = data_object.check_data_validity()
        if not invalid_data_error is None:
            if not list_is_empty(invalid_data_error.error_list):
                print invalid_data_error.msg
                print "______________"
                for e in filter(None, invalid_data_error.error_list):
                    print e.msg
                    print "______________"
                self.fail(
                    "Failed the test because there is(are) " + str(len(filter(None, invalid_data_error.error_list))) +
                    " error(s) while there should be none.")
        else:
            print "Test completed successfully!"

    def negative_test_stub_for_model_data_validity(self, data_object, number_of_expected_errors, header_string=None):
        """
        This method is used by all model tests that test on data validity for model objects.
        Here, the default check_data_validity method that every model class implements will
        be called and it's results saved. If there are any errors, this method will see if
        the number is equal to the number_of_expected_errors and fail if it's not. This also
        means that (currently), there is no way to test if a specific error is caused by the
        data object.

        If there are errors, a "success" message will be printed that will display which error
        has been successfully detected.

        Additionally, a header string can be passed that should be printed. This can contain
        a simple indication of what is tested (which class) which will improve read-ability
        of test results.

        :param data_object:
            The object that needs to be tested for data validity. Must belong to a class
            that implements the check_data_validity method and all errors that this method
            produce must have a msg field implemented that contains a description of what
            the error is.
        :param number_of_expected_errors:
            The number of errors that are expected to be found when the data validity of the
            given data object is tested.
        :param header_string:
            (Optional) A string that should be printed before anything else, that can display
             what (type of object) will be tested. Used to improve read-ability of test results.
        """
        if header_string is not None:
            print header_string
        invalid_data_error = data_object.check_data_validity()
        if list_is_empty(invalid_data_error.error_list) or \
                (len(filter(None, invalid_data_error.error_list)) is not number_of_expected_errors):
            self.fail("Failed to find the specified amount of errors: expected " + str(
                number_of_expected_errors) + ", but found " + str(len(filter(None, invalid_data_error.error_list))))
        else:
            print "Successfully detected the error: " + str(data_object)
            print invalid_data_error.msg
            for e in filter(None, invalid_data_error.error_list):
                print e.msg

    def positive_test_stub_handler(self, path, request_type, response_body_should_be_defined=True,
                                   expected_content_type='application/json', body_data_should_have_results=True,
                                   data_dict=None):
        """
        This method serves as a base stub for all positive request handler unit tests. It will get
        the response from the testapp on the given URL path and the given request type, or fail
        if either the request type is invalid (no HTTP request) or the url path is not found
        in the testapp (which would probably mean that the path has not been set-up with
        the set_up_test_server_with_custom_routes method to begin with).

        If the testapp gives a response, this method will check if the response exists, has a 200
        status code, if the content_type matched the type that is expected and (optionally)
        if the body is defined. Any other tests should be executed by the specific test method.

        :param path:
            The path parameter specifies to which url the testapp should post the request.
        :param request_type:
            A string that specifies what type of request should be sent to the testapp
            (i.e. a GET-, POST-, PUT- or DELETE request). Will be transformed to lowercase.
            Read the documentation at the following link to see which requests are valid:
            http://webtest.readthedocs.org/en/latest/testapp.html

            Note on the post_json method: this expects the data in a dictionary/list format, not a dumped
            json string!
        :param response_body_should_be_defined:
            (Optional) Used to indicate whether this method should also check if the given response's
            body field is set (is not None). Default value is True.
        :param expected_content_type:
            (Optional) A string that indicates what the type of the response should be
            (i.e. 'text/html', 'application/json' etc.). If this is set to None, this check will be
            skipped. Default value is "application/json".
        :param body_data_should_have_results:
            (Optional) Used to indicate whether this method should also check if the given response's
            body field actually contains results (used for checking non empty lists and dictionaries).
            Default value is True.
        :param data_dict:
            Dictionary or List object that is to be given along with the response to the test server.
            This will be None by default, and as long as it's None, no data will be set (so not setting
            this parameter won't result in a Null value being set as the requests' body).
            This parameter will _NOT_ be checked to see if it's valid JSON data (list or dict), since this is
            the responsibility of the handler and this would give problems when writing negative tests. If anything
            but a dict or list is passed, this will raise an error in the testapp, so check your input!
        """
        #Retrieve the correct request reference
        try:
            lowercase_request_type = request_type.lower()
            request_reference = getattr(self.testapp, lowercase_request_type)
        except AttributeError:
            self.fail("No valid method found for the request_type of '" + str(request_type) +
                      "'.\nrequest_type must be a string that indicates what type of request should be " +
                      "sent to the testapp (i.e. 'get', 'post' etc.).")

        #Send the request that is stored in request_reference with the path parameter and optionally,
        # the json_data parameter
        try:
            if data_dict is None:
                response = request_reference(path)
            else:
                response = request_reference(path, data_dict)
        except webtest.AppError as appError:
            self.fail("Failed to send a request to the testapp. Expected a valid response, but got an exception:"
                      "\n\tError Type:" + str(type(appError).__name__) +
                      "\n\tError Message:" +
                      "\n\t\t" + str(appError.message))
        except Exception:
            self.fail("Error while trying to send the request to the testapp. Are you sure that the given request-type "
                      "is a valid http request method (i.e. GET, POST, PUT or DELETE)?")

        #Execute the basic tests
        self.assertIsNotNone(response)
        self.assertEqual(response.status_int, 200)

        #Execute the conditional tests
        if expected_content_type is not None:
            self.assertEqual(response.content_type, expected_content_type)
        if response_body_should_be_defined:
            self.assertIsNotNone(response.body)
        if body_data_should_have_results:
            try:
                body_data = json.loads(response.body)
            except ValueError:
                self.fail("Test failed! The response body did not contain valid JSON data.")
            self.assertTrue(len(body_data) > 0,
                            "Test failed! There should be results in the response, but none were found.")

        return response

    def negative_test_stub_handler(self, path, request_type, expected_error_code, data_dict=None):
        """
        This method serves as a base stub for all negative request handler unit tests. It will get
        the response from the testapp on the given URL path and the given request type, or fail
        if either the request type is invalid (no HTTP request) or the url path is not found
        in the testapp (which would probably mean that the path has not been set-up with
        the set_up_test_server_with_custom_routes method to begin with).

        If the testapp cannot execute the request, this method will go on to check if the occured error
        is actually initialized properly and has the specified error code. If the error code that is expected
        is present in the occurred error, the test has passed and a short "success" message will be printed.

        If a valid response is given by the testapp (meaning that there was no error where there should be one),
        the test will fail with a message that indicates this.

        :param path:
            The path parameter specifies to which url the testapp should post the request.
        :param request_type:
            A string that specifies what type of request should be sent to the testapp
            (i.e. a GET-, POST-, PUT- or DELETE request). Will be transformed to lowercase.
            Read the documentation at the following link to see which requests are valid:
            http://webtest.readthedocs.org/en/latest/testapp.html

            Note on the post_json method: this expects the data in a dictionary/list format, not a dumped
            json string!
        :param expected_error_code:
            The integer status code that should be returned by the testapp when the specified request is sent to the
            specified url path (i.e. 400, 500, 404 etc.). Will be checked for using a string comparison, since
            direct comparison is not (yet) supported in the webtest framework.
        :param data_dict:
            Dictionary or List object that is to be given along with the response to the test server.
            This will be None by default, and as long as it's None, no data will be set (so not setting
            this parameter won't result in a Null value being set as the requests' body).
            This parameter will _NOT_ be checked to see if it's valid JSON data (list or dict), since this is
            the responsibility of the handler and this would give problems when writing negative tests. If anything
            but a dict or list is passed, this will raise an error in the testapp, so check your input!
        """
        #Retrieve the correct request reference
        try:
            lowercase_request_type = request_type.lower()
            request_reference = getattr(self.testapp, lowercase_request_type)
        except AttributeError:
            self.fail("No valid method found for the request_type of '" + str(request_type) +
                      "'.\nrequest_type must be a string that indicates what type of request should be " +
                      "sent to the testapp (i.e. 'get', 'post' etc.).")
        response = None

        #Send the request that is stored in request_reference with the path parameter and optionally,
        # the json_data parameter
        try:
            if data_dict is None:
                response = request_reference(path)
            else:
                response = request_reference(path, data_dict)
        except webtest.AppError as appError:
            #We want this to happen! See if the appError variable is properly initialized.
            self.assertIsNotNone(appError)
            self.assertTrue(
                str(expected_error_code)
                in appError.message)  # Bit ugly, but only way possible to check for the given code specifically
            print "Succesfully detected an error on path: '" + path + "':"
            print "\t" + appError.message
        except Exception:
            self.fail("Error while trying to send the request to the testapp. Are you sure that the given request-type"
                      "is a valid http request method (i.e. GET, POST, PUT or DELETE)?")
        if response is not None:
            self.fail("Failed to detect an error with the path '" + path + "'.")


def list_is_empty(collection_object):
    """
    Helper method that will return true if a list object is either None or has no contents.

    :param collection_object:
        The object that has to be tested to see if it is None or has no
        contents. Both lists and dictionaries are supported. These are
        considered to be empty if there are no objects within (list)
        or if there are no key-value pairs present (dict)
        (meaning that a Key with a None value still counts!).
    """
    if collection_object is not None and len(filter(None, collection_object)) > 0:
        return True
    return False
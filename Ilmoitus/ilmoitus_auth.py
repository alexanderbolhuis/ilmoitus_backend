__author__ = 'Robin'

import hashlib
import random
import string
import webapp2 as webapp
import logging


class BaseRequestHandler(webapp.RequestHandler):
    """
    Wrapper class that will allow all other handler classes to make easily read what the
    limit and/or offset is for a request
    check login
    fetch loggedin user
    supply with the correct headers with an option request (supports up to 2 get params!)
    """
    def is_logged_in(self):
        result = get_current_person(self)
        return result["user_is_logged_in"]

    def logged_in_person(self):
        result = get_current_person(self)
        return result["person_value"]

    def check_hr(self):
        if self.logged_in_person().class_name != "human_resources":
            give_error_response(self, 401, "U bent niet ingelogd als HR",
                                           "User is not HR")

    def options(self, optionalkey=None, optionalkey2=None):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE'

    def get_header(self, key):
        header = self.request.get(key, default_value=None)
        return header

    def get_header_limit(self):
        limit = self.request.get("limit", default_value=20)
        return limit

    def get_header_offset(self):
        offset = self.request.get("offset", default_value=0)
        return offset

    def handle_exception(self, exception, debug):
        """
        Overrides function in webapp.RequestHandler.

        This function will catch any HTTP exceptions that can be raised by a .abort() function call within
        a handler that inherits from the BaseRequestHandler class. When this happens, this function will
        log the request and if the application is in debug mode, also the exception (basically the complete
        stack trace).

        Lastly, this function will write the full body of the request and set the status of the response
        to the code of the exception. It's important to note that the body of the request is used as a
        response, since it's through this property that any data will be sent back to the user (such as
        a message indicating what went wrong, status and error codes, etc.). This is also the only real
        custom functionality that this function provides (the rest is default, but a call to the base method
        could cause problems in some cases).

        :param exception: The exception that was raised by this handler or any handler that inherits from this handler.

        :param debug: Boolean indicating whether the application is in debug mode or not. Will be automatically
            detected.
        """
        logging.debug(self.request)
        if debug:
            logging.exception(exception)

        self.response.write(self.request.body)
        try:
            self.response.set_status(exception.code)
        except AttributeError:
            #The caught exception was not a HTTPException; we don't know how to handle this so just raise it again
            raise exception


from response_module import *
from ilmoitus_model import *


def get_current_person(request_handler):
    """
     Global function that will retrieve the user that is currently logged in (through token based Auth)
     and fetch the person model object of this application that belongs to it through the email field.

     :returns: A dictionary containing two key-value pairs:
         -"user_is_logged_in": Boolean that indicates whether a user is logged into the users API of Google.

         -"person_value": Model object of the Person type
    """

    # Fetch header from request
    auth_header = request_handler.request.headers["Authorization"]

    if auth_header is not None:
        auth_split = auth_header.split(",")

        # Check if header consists of 2 parts (user_id,token)
        if len(auth_split) == 2:
            auth_token = auth_split[1]
            auth_id = 0

            try:
                auth_id = long(auth_split[0])
            except ValueError:
                return auth_error(request_handler)

            # Query user
            query_result = Person.get_by_id(auth_id)

            if query_result is not None:
                if query_result.token is not None and check_secret(auth_token, query_result.token):
                    return {"user_is_logged_in": True, "person_value": query_result}

    return auth_error(request_handler)


def auth_error(handler):
    #Send 401 right away
    give_error_response(handler, 401, "U bent niet ingelogd", "token not found or accepted")


def auth(email, password):
    #TODO: Figure out how not to do this in unittests
    #time.sleep(1)

    person_query = Person.query(Person.email == email)
    query_result = person_query.get()
    if query_result is not None and check_secret(password, query_result.password):
        # User passed the test, generate token and save hashed version to database
        raw_token = gen_salt(16);
        query_result.token = hash_secret(raw_token)
        query_result.put()

        return {"passed": True, "person_value": query_result, "token": (str(query_result.key.integer_id()) + ',' + raw_token)}

    return {"passed": False}


# Generates secret string with input + salt
def hash_secret(input_token):
    salt = gen_salt(16)

    m = hashlib.sha256()
    m.update(salt)
    m.update(input_token)

    # Append salt for retrieving
    return salt + ',' + m.hexdigest()


# Generates secret string with input + salt
def check_secret(input_token, check_token):
    token_parts = check_token.split(',')
    if len(token_parts) != 2:
        return False

    m = hashlib.sha256()
    m.update(token_parts[0])
    m.update(input_token)

    # Compare tokens
    return token_parts[1] == m.hexdigest()


def gen_salt(size, letters=string.letters + string.digits):
    chars = []

    for i in range(size):
        chars.append(random.choice(letters))

    return "".join(chars)


class AuthorizationStatusHandler(BaseRequestHandler):
    def get(self):
        result = get_current_person(self)

        if result["user_is_logged_in"]:
            give_response(self, json.dumps({"person_id": result["person_value"].key.integer_id(), "is_logged_in": True}))


class LoginHandler(BaseRequestHandler):
    def post(self):
        result = auth(self.request.POST["email"], self.request.POST["password"])

        if result["passed"]:
            person = result["person_value"]
            give_response(self, json.dumps({"person_id": person.key.integer_id(), "is_logged_in": True, "token": result["token"]}))
        else:
            give_response(self, json.dumps({"is_logged_in": False}))


class LogoutHandler(BaseRequestHandler):
    def get(self):
        person = self.logged_in_person()
        person.token = ""
        person.put()

        give_response(self, json.dumps({"person_id":0, "is_logged_in": False}))

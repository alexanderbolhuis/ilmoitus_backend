__author__ = 'Robin'

from error_response_module import give_error_response
from ilmoitus_model import *
from response_module import *
import ilmoitus_model
import response_module
import hashlib
import random
import string
import time


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


def auth_error(request_handler):
    #Send 401 right away
    give_error_response(request_handler, 401, "U bent niet ingelogd", "token not found or accepted")
    return {"user_is_logged_in": False, "person_value": None}


def auth(email, password):
    #TODO: Figure out how not to do this in unittests
    time.sleep(1)

    person_query = ilmoitus_model.Person.query(ilmoitus_model.Person.email == email)
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
        pass
__author__ = 'Robin'

import ilmoitus_model
import hashlib
import random
import time


def get_current_person(request_handler, class_name=None):
    """
     Global function that will retrieve the user that is currently logged in (through token based Auth)
     and fetch the person model object of this application that belongs to it through the email field.

     :param class_name: (Optional) A reference to a person model class that should be used to find
     the model class object that belongs to the logged in user. If not provided, model.Person will be used.

     :returns: A dictionary containing two key-value pairs:
         -"user_is_logged_in": Boolean that indicates whether a user is logged into the users API of Google.

         -"person_value": Model object of the Person type (or any subclass, indicated by the person_class_reference
        parameter). If there is either no user logged in, this will be None
    """

    # Default return
    return_data = {"user_is_logged_in": False, "person_value": None}

    # Fetch header from request
    auth_header = request_handler.request.headers["Authorization"]

    if auth_header is not None:
        auth_split = auth_header.split(" ")

        # Check if header consists of 2 parts (userid token)
        if len(auth_split) == 2:
            auth_email = auth_split[0]
            auth_token = auth_split[1]

            # Query user
            if class_name is None:
                person_query = ilmoitus_model.Person.query(ilmoitus_model.Person.email == auth_email)
            else:
                person_query = ilmoitus_model.Person.query(ilmoitus_model.Person.email == auth_email,
                                                           ilmoitus_model.Person.class_name == class_name)

            query_result = person_query.get()
            if query_result is not None:
                if query_result.token is not None and check_secret(auth_token, query_result.token):
                    return_data = {"user_is_logged_in": True, "person_value": query_result}

    return return_data


def authencate(email, password):
    person_query = ilmoitus_model.Person.query(ilmoitus_model.Person.email == email)
    query_result = person_query.get()
    if query_result is not None:
        if check_secret(password, query_result.password):
            # User passed the test, generate token and save hashed version to database
            raw_token = gen_salt(16);
            query_result.token = hash_secret(raw_token);
            query_result.put()

            time.sleep(1)
            return {"passed": True, "person_value": query_result, "token": (query_result.email + ' ' + raw_token)}

    time.sleep(1)
    return {"passed": False }


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


def gen_salt(size):
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars=[]
    for i in range(size):
        chars.append(random.choice(ALPHABET))

    return "".join(chars)
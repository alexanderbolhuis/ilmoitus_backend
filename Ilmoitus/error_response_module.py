__author__ = 'Sjors van Lemmen'
import json


def set_non_empty_key_value_pairs_in_dict(dictionary_to_build, dictionary_to_set):
    """
     Function that will take all key : value pairs from the dictionary_to_set parameter and
     (if the value of that pair is not None, larger than 0 if the key concerns a number and
     not an empty String if the key does not concern a number) puts them in the
     dictionary_to_build object, which is returned afterwards.


     :param dictionary_to_build: The dictionary object that needs to have it's key : value
        pairs set. Is always returned afterwards.

     :param dictionary_to_set: The dictionary object that will have it's key : value pairs set
        into the dictionary_to_build parameter. Key : values will only be set if the value is not
        None, larger than 0 if the key concerns an integer value (status_code and error_code) and
        is not an empty String if the key does not concern an integer value.
    """
    for key in dictionary_to_set:
        value = dictionary_to_set[key]
        if value is not None:
            if key in ["status_code", "error_code"]:
                if value > 0:
                    dictionary_to_build[key] = value
            else:
                if value != "":
                    dictionary_to_build[key] = value
    return dictionary_to_build


def give_error_response(request_handler, status_code, user_message, developer_message="No developer message available",
                        error_code=0, more_info="No additional information available"):
    # Create a dictionary with all the parameters and their values, except the handler
    param_values = {"status_code": status_code,
                    "developer_message": developer_message,
                    "user_message": user_message,
                    "error_code": error_code,
                    "more_info": more_info}

    # Create an empty dictionary that we will use to respond with
    response_data = {}

    response_data = set_non_empty_key_value_pairs_in_dict(response_data, param_values)

    request_handler.response.headers['Content-Type'] = "application/json"
    request_handler.response.body = json.dumps(response_data)

    request_handler.abort(status_code)
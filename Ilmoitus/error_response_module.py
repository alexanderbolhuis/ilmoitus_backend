__author__ = 'Sjors van Lemmen'
import json


def give_error_response(request_handler, status_code, user_message, developer_message=None, error_code=0,
                        more_info=None):
    """
     Function that will use a request handler that it receives to give an error message. This message
     will have it's HTTP status code set according to the parameter value, but this function will
     still provide response data. This data consists of several fields that can be used in the front-end
     to provide more detailed and useful error messages to the user.

     After setting all these fields, the handler's abort function is called, which will raise an HTTP
     exception that can be caught by an handle_exception function override in that request handler.
    """
    response_data = {"status_code": status_code,
                     "developer_message": developer_message,
                     "user_message": user_message,
                     "error_code": error_code,
                     "more_info": more_info}

    request_handler.response.headers['Content-Type'] = "application/json"
    request_handler.response.body = json.dumps(response_data)

    request_handler.abort(status_code)
__author__ = 'Sjors van Lemmen'
import json


def give_error_response(request_handler, status_code, user_message, developer_message=None, error_code=0,
                        more_info=None):
    response_data = {"status_code": status_code,
                     "developer_message": developer_message,
                     "user_message": user_message,
                     "error_code": error_code,
                     "more_info": more_info}

    request_handler.response.headers['Content-Type'] = "application/json"
    request_handler.response.body = json.dumps(response_data)

    request_handler.abort(status_code)
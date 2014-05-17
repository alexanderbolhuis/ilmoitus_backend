__author__ = 'Sjors van Lemmen'
import json
import logging
import ilmoitus_auth
import webapp2 as webapp


class BaseRequestHandler(webapp.RequestHandler):
    """
    Wrapper class that will allow all other handler classes to make easily read what the
    limit and/or offset is for a request
    """
    def is_logged_in(self):
        result = ilmoitus_auth.get_current_person(self)
        return result["user_is_logged_in"]

    def logged_in_person(self):
        result = ilmoitus_auth.get_current_person(self)
        return result["person_value"]

    def options(self, optionalkey=None):
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


def respond_with_object_details_by_id(request_handler, class_reference, object_id):
    request_handler.response.headers['Access-Control-Allow-Origin'] = '*'
    safe_id = 0
    try:
        safe_id = long(object_id)
    except ValueError:
        #TODO: give proper error response here
        request_handler.abort(500)

    item = class_reference.get_by_id(safe_id)
    if item is None:
        #TODO: give proper error response here
        request_handler.abort(404)
    give_response(request_handler, item.get_object_json_data())


def respond_with_object_collection_with_query(request_handler,  query):
    request_handler.response.headers['Access-Control-Allow-Origin'] = '*'

    query_result = query.fetch(limit=request_handler.get_header_limit(), offset=request_handler.get_header_offset())
    respond_with_existing_model_object_collection(request_handler, query_result)


def respond_with_object_collection_by_class(request_handler, class_reference, limit, offset, class_name=None):
    request_handler.response.headers['Access-Control-Allow-Origin'] = '*'
    if class_name is None:
        query = class_reference.query()
    else:
        query = class_reference.query().filter(class_reference.class_name == class_name)
    query_result = query.fetch(limit=limit, offset=offset)
    if len(query_result) > 0:
        #important to dump the result of the map; this takes care of the wrapper list object that contains all items
        give_response(request_handler, json.dumps(map(lambda item: item.get_object_as_data_dict(), query_result)))
    else:
        give_response(request_handler, None)


def respond_with_existing_model_object_collection(request_handler, collection):
    request_handler.response.headers['Access-Control-Allow-Origin'] = '*'
    if len(collection) > 0:
        #important to dump the result of the map; this takes care of the wrapper list object that contains all items
        give_response(request_handler, json.dumps(map(lambda item: item.get_object_as_data_dict(), collection)))
    else:
        give_response(request_handler, None)


def give_response(request_handler, json_data):
    request_handler.response.headers['Access-Control-Allow-Origin'] = '*'
    request_handler.response.headers['Content-Type'] = "application/json"
    if json_data is not None:
        request_handler.response.write(json_data)
    else:
        #TODO: give proper error response here
        request_handler.abort(404)


def give_hard_response(request_handler, response_data):
    """
        Gives a "hard" response, meaning that it could be anything from raw JSON data to HTML data.
        This function should NOT be used by anything other than a quick (and obviously very dirty) test.
    """
    request_handler.response.headers['Access-Control-Allow-Origin'] = '*'
    request_handler.response.write(response_data)
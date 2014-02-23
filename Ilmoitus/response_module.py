__author__ = 'Sjors van Lemmen'
import json


def respond_with_object_details_by_id(request_handler, class_reference, object_id):
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
    #TODO: make generic method in model that will dump JSON data
    give_response(request_handler, json.dumps(item))


def respond_with_object_collection_by_class(request_handler, class_reference, limit, offset):
    query = class_reference.query()
    result = query.fetch(limit, offset)
    give_response(request_handler, json.dumps(result))


def give_response(request_handler, json_data):
    request_handler.response.headers['Content-Type'] = "application/json"
    if json_data is not None:
        request_handler.response.out.wirte(json_data)
    else:
        #TODO: give proper error response here
        request_handler.abort(404)
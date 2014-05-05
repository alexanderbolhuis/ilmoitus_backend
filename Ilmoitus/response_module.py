__author__ = 'Sjors van Lemmen'
import json


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
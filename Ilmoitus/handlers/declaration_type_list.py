__author__ = 'RobinB'

from ilmoitus_auth import *
from response_module import *
from mail_module import *


class AllDeclarationTypesHandler(BaseRequestHandler):
    def get(self):
        query = ilmoitus_model.DeclarationType.query()
        query_result = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

        if len(query_result) != 0:
            response_module.give_response(self, json.dumps(
                map(lambda declaration_type: declaration_type.get_object_as_data_dict(), query_result)))
        else:
            give_error_response(self, 404, "There are no DeclarationTypes",
                                "Add some DeclarationTypes to the data store")


class AllDeclarationTypeSubTypeHandler(BaseRequestHandler):
    def get(self, declaration_type_id):
        safe_id = 0
        try:
            safe_id = long(declaration_type_id)
        except ValueError:
            give_error_response(self, 500, "the given id isn't an int (" + str(declaration_type_id) + ")")

        item = ilmoitus_model.DeclarationType.get_by_id(safe_id)

        if item is None:
            give_error_response(self, 404, "there is no declarationType with that id")

        if len(item.sub_types) is 0:
            give_error_response(self, 404, "there are no DeclarationSubTypes associated to this DeclarationType")

        query = ilmoitus_model.DeclarationSubType.query(ilmoitus_model.DeclarationSubType.key.IN(item.sub_types))
        sub_types = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())
            #[res for res in query.fetch() if res.key in item.sub_types]

        if len(sub_types) is 0:
            give_error_response(self, 404, "there are no DeclarationSubTypes associated to this DeclarationType")

        response_module.give_response(self, json.dumps(map(lambda sub_type: sub_type.get_object_as_data_dict(),
                                                           sub_types)))


class AllDeclarationSubTypesHandler(BaseRequestHandler):
    def get(self):
        query = ilmoitus_model.DeclarationSubType.query()

        query_result = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

        if query_result is None:
            give_error_response(self, 404, "there are no DeclarationSubTypes",
                                "insert some DeclarationSubTypes in the datastore")
        else:
            response_module.respond_with_existing_model_object_collection(self, query_result)
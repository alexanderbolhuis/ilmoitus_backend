__author__ = 'RobinB'

from error_checks import *


class AllDeclarationTypesHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            respond_with_object_collection_with_query(self, DeclarationType.query())


class AllDeclarationTypeSubTypeHandler(BaseRequestHandler):
    def get(self, declaration_type_id):
        if self.is_logged_in():
            item = find_declaration_type(self, declaration_type_id)
            respond_with_object_collection_with_query(self, DeclarationSubType.query(DeclarationSubType.key.IN(item.sub_types)))


class AllDeclarationSubTypesHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            respond_with_object_collection_with_query(self, DeclarationSubType.query())
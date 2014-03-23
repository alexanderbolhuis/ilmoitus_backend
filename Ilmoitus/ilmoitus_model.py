__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.ndb.key import Key
from datetime import datetime
import json


# Department Model class
class Department(ndb.Model):
    name = ndb.StringProperty

    def details(self):
        return {'name': self.name}


# Person Model class
class Person(ndb.Model):
    class_name = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    employee_number = ndb.IntegerProperty()
    department = ndb.KeyProperty(kind=Department)
    supervisor = ndb.KeyProperty(kind="Person")

    all_custom_properties = ["first_name", "last_name", "email", "employee_number", "department",
                             "supervisor"]
    permissions = {"user": ["first_name", "last_name", "email"],
                   "employee": ["first_name", "last_name", "email", "employee_number", "department",
                                "supervisor"],
                   "supervisor": ["first_name", "last_name", "email", "employee_number", "department",
                                  "supervisor"],
                   "human_resources": ["first_name", "last_name", "email", "employee_number", "department",
                                       "supervisor"]}

    def get_object_as_data_dict(self):
        return dict({'id': self.key.integer_id(), 'class_name': self.class_name}.items() +
                    property_not_none_key_value_pair_with_permissions(self).items())

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())

    def __setattr__(self, key, value):
        if key in self.all_custom_properties:
            object.__setattr__(self, key, self.handle_custom_property_set_operation(self.permissions, key, value))
        else:
            object.__setattr__(self, key, value)

    def handle_custom_property_set_operation(self, permissions, key, value):
        #todo: make global function?
        try:
            default_value = self.__dict__[key]
        except KeyError:
            default_value = None
        # check if the requested key exists within the list of the permission dictionary that belongs to this class'
        #list
        if key in permissions[self.class_name]:
            #It's allowed; return the new value
            return value
        else:
            return default_value


# OpenDeclaration Model class
class Declaration(ndb.Model):
    class_name = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    created_by = ndb.KeyProperty(kind=Person)
    assigned_to = ndb.KeyProperty(kind=Person)
    comment = ndb.StringProperty()
    declined_by = ndb.KeyProperty(kind=Person)
    submitted_to_hr_by = ndb.KeyProperty(kind=Person)
    approved_by = ndb.KeyProperty(kind=Person)

    #'Static' dictionary with readable states
    readable_states = {
        "open_declaration": "Open",
        "locked_declaration": "In behandeling",  #User story (leidinggevende kan declaratie locken)
        "declined_declaration": "Afgekeurd leidinggevende",
        "approved_declaration": "Goedgekeurd leidinggevende",
        "closed_declaration": "Afgekeurd",  #Declined by hr I suppose?
        "approved_declaration_hr": "Goedgekeurd",
    }

    #'Static' dictionary with readable states
    readable_states = {
                    "open_declaration": "Open",
                    "locked_declaration": "In behandeling",                 #User story (leidinggevende kan declaratie locken)
                    "declined_declaration": "Afgekeurd leidinggevende",
                    "approved_declaration": "Goedgekeurd leidinggevende",
                    "closed_declaration": "Afgekeurd",                      #Declined bij hr i suppose?
                    "approved_declaration_hr": "Goedgekeurd",
    }

    all_custom_properties = ["created_at", "created_by", "assigned_to", "comment", "declined_by",
                             "submitted_to_hr_by"]
    permissions = {"open_declaration": ["created_at", "created_by", "assigned_to", "comment"],
                   "closed_declaration": ["created_at", "created_by", "assigned_to", "comment", "declined_by",
                                          "submitted_to_hr_by"],
                   "declined_declaration": ["created_at", "created_by", "assigned_to", "comment", "declined_by"],
                   "approved_declaration": ["created_at", "created_by", "assigned_to", "comment", "submitted_to_hr_by",
                                            "approved_by"]}

    def get_object_as_data_dict(self):
        return dict({'id': self.key.integer_id(),
                     'class_name': self.class_name,
                     "state": self.readable_state()}.items() +
                    property_not_none_key_value_pair_with_permissions(self).items())

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())

    def readable_state(self):
        return self.readable_states[self.class_name];


    def __setattr__(self, key, value):
        """
         Function that overrides the default setting of properties within python. Take the following code:

         class Foo(object):
            bar = 5

        baz = Foo()
        baz.bar = 10

        The statement baz.bar = 10 will now come in this method where things can be checked before deciding to set
        the property (or not).

        This implementation specifically will check if the requested set operation for a specific property is
        allowed with the current value of the class_name property. If that value is "open_declaration" for instance,
        the declined_by property is not allowed to be set (but is when the class_name property is set to
        "closed_declaration").

        Uses the handle_custom_property_set_operation function to actually determine if the value should be changed
        or not.
        """
        if key in self.all_custom_properties:
            object.__setattr__(self, key, self.handle_custom_property_set_operation(self.permissions, key, value))
        else:
            object.__setattr__(self, key, value)

    def handle_custom_property_set_operation(self, permissions, key, value):
        #todo: make global function?
        try:
            default_value = self.__dict__[key]
        except KeyError:
            default_value = None
        # check if the requested key exists within the list of the permission dictionary that belongs to this class'
        #list
        if key in permissions[self.class_name]:
            #It's allowed; return the new value
            return value
        else:
            return default_value

    def all(self):
        return Declaration.key


# DeclarationSubType Model class
class DeclarationSubType(ndb.Model):
    name = ndb.StringProperty()
    max_cost = ndb.IntegerProperty()  # Optional


# DeclarationType Model class
class DeclarationType(ndb.Model):
    declaration_sub_types = ndb.KeyProperty(kind=DeclarationSubType)

    def get_object_as_data_dict(self):
        return {'declaration_sub_types': self.declaration_sub_types.integer_id()}

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


# DeclarationLine Model class
class DeclarationLine(ndb.Model):
    declaration = ndb.KeyProperty(kind=Declaration)
    receipt_date = ndb.StringProperty()  # DateProperty?
    cost = ndb.IntegerProperty()
    declaration_type = ndb.KeyProperty(kind=DeclarationType)
    declaration_sub_type = ndb.KeyProperty(kind=DeclarationSubType)

    def get_object_as_data_dict(self):
        return {'declaration': self.declaration.key.integer_id(),
                'receipt_date': self.receipt_date,
                'cost': self.cost,
                'declaration_type': self.declaration_type.integer_id(),
                'declaration_sub_type': self.declaration_sub_type.integer_id()}

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


class Attachment(ndb.Model):
    ndb.KeyProperty(kind=Declaration)
    blobstore.BlobReferenceProperty(required=True)

    def get_object_as_data_dict(self):
        return {'': ""}  # TODO get_object_as_data_dict

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())

def property_not_none_key_value_pair_with_permissions(class_reference):
    key_value_pair = {}
    if class_reference is not None and class_reference.permissions is not None:
        permissions = class_reference.permissions[class_reference.class_name]
        if permissions is not None:
            for prop in permissions:
                value = getattr(class_reference, prop)
                if value is not None:
                    value_type = type(value)
                    if type(value) is Key:
                        value = value.integer_id()
                    elif type(value) is datetime:
                        value = str(value)
                    key_value_pair = dict(key_value_pair.items() + {prop: value}.items())

    return key_value_pair

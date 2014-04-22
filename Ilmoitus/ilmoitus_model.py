__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import json
import collections

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
    password = ndb.StringProperty()
    token = ndb.StringProperty()
    employee_number = ndb.IntegerProperty()
    department = ndb.KeyProperty(kind=Department)
    supervisor = ndb.KeyProperty(kind="Person")

    all_custom_properties = ["first_name", "last_name", "email", "employee_number", "department",
                             "supervisor"]
    permissions = {"user": ["first_name", "last_name", "email", "class_name"],
                   "employee": ["first_name", "last_name", "email", "employee_number", "department",
                                "supervisor", "class_name"],
                   "supervisor": ["first_name", "last_name", "email", "employee_number", "department",
                                  "supervisor", "class_name"],
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
    assigned_to = ndb.KeyProperty(kind=Person, repeated=True)
    comment = ndb.StringProperty()
    supervisor_comment = ndb.StringProperty()
    human_resources_comment = ndb.StringProperty()
    declined_by = ndb.KeyProperty(kind=Person)
    submitted_to_human_resources_by = ndb.KeyProperty(kind=Person)
    locked_at = ndb.DateTimeProperty()
    sent_to_human_resources_at = ndb.DateTimeProperty()
    supervisor_declined_at = ndb.DateTimeProperty()
    supervisor_approved_at = ndb.DateTimeProperty()
    human_resources_approved_at = ndb.DateTimeProperty()
    human_resources_declined_at = ndb.DateTimeProperty()
    will_be_payed_out_on = ndb.DateProperty()
    human_resources_declined_by = ndb.KeyProperty(kind=Person)
    supervisor_approved_by = ndb.KeyProperty(kind=Person)
    human_resources_approved_by = ndb.KeyProperty(kind=Person)


    #'Static' dictionary with readable states
    readable_states = {
        "open_declaration": "Open",
        "locked_declaration": "In behandeling",
        "supervisor_declined_declaration": "Afgekeurd leidinggevende",
        "supervisor_approved_declaration": "Goedgekeurd leidinggevende",
        "human_resources_declined_declaration": "Afgekeurd",
        "human_resources_approved_declaration": "Goedgekeurd",
    }

    # this property is used to check the permissions against
    all_custom_properties = ["created_at", "created_by", "assigned_to", "comment", "supervisor_comment",
                             "human_resources_comment", "declined_by", "submitted_to_human_resources_by", "locked_at",

                             "sent_to_human_resources_at", "supervisor_declined_at", "supervisor_approved_at",
                             "human_resources_approved_at", "human_resources_declined_at", "will_be_payed_out_on",
                             "human_resources_approved_by"]

    permissions = {"open_declaration": ["created_at", "created_by", "assigned_to", "comment"],

                   "locked_declaration": ["created_at", "created_by", "assigned_to", "comment", "locked_at",

                                          "supervisor_comment"],

                   "supervisor_declined_declaration": ["created_at", "created_by", "assigned_to", "comment",
                                                       "locked_at", "declined_by", "supervisor_declined_at",
                                                       "supervisor_comment"],

                   "supervisor_approved_declaration": ["created_at", "created_by", "assigned_to", "comment",
                                                       "locked_at", "submitted_to_human_resources_by",
                                                       "supervisor_approved_at", "supervisor_approved_by",
                                                       "sent_to_human_resources_at", "supervisor_comment"],

                   "human_resources_declined_declaration": ["created_at", "created_by", "assigned_to", "comment",
                                                            "locked_at", "submitted_to_human_resources_by",
                                                            "supervisor_approved_at", "supervisor_approved_by",
                                                            "sent_to_human_resources_at", "declined_by",
                                                            "supervisor_comment", "human_resources_comment",
                                                            "human_resources_declined_at"],

                   "human_resources_approved_declaration": ["created_at", "created_by", "assigned_to", "comment",
                                                            "locked_at", "submitted_to_human_resources_by",
                                                            "supervisor_approved_at", "supervisor_approved_by",
                                                            "sent_to_human_resources_at", "supervisor_comment",
                                                            "will_be_payed_out_on", "human_resources_comment",
                                                            "human_resources_approved_by",
                                                            "human_resources_approved_at"]}

    def get_object_as_data_dict(self):
        return dict({'id': self.key.integer_id(),
                     'class_name': self.class_name,
                     "state": self.readable_state()}.items() +
                    property_not_none_key_value_pair_with_permissions(self).items())

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())

    def readable_state(self):
        return self.readable_states[self.class_name]

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


# DeclarationSubType Model class
class DeclarationSubType(ndb.Model):
    name = ndb.StringProperty()
    max_cost = ndb.IntegerProperty()  # Optional

    all_custom_properties = ['name', 'max_cost']

    def get_object_as_data_dict(self):
        return {'id': self.key.integer_id() + property_not_none_key_value_pair(self,
                                                                               self.all_custom_properties).items()}

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


# DeclarationType Model class
class DeclarationType(ndb.Model):
    name = ndb.StringProperty()
    sub_types = ndb.KeyProperty(kind=DeclarationSubType, repeated=True)

    all_custom_properties = ['name', 'sub_types']

    def get_object_as_data_dict(self):
        return property_not_none_key_value_pair(self, self.all_custom_properties)

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


# DeclarationLine Model class
class DeclarationLine(ndb.Model):
    declaration = ndb.KeyProperty(kind=Declaration)
    receipt_date = ndb.DateTimeProperty()
    cost = ndb.IntegerProperty()
    declaration_sub_type = ndb.KeyProperty(kind=DeclarationSubType)

    all_custom_properties = ['declaration', 'receipt_date', 'cost', 'declaration_sub_type']

    def get_object_as_data_dict(self):
        return property_not_none_key_value_pair(self, self.all_custom_properties)

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


class Attachment(ndb.Model):
    declaration = ndb.KeyProperty(kind=Declaration)
    blob = ndb.BlobKeyProperty(required=True)

    def get_object_as_data_dict(self):
        return {'id': self.key.integer_id(), 'declaration': self.declaration.integer_id(),
                'blob': self.blob}
        #TODO make it work, this can't be tested yet because we can't simulate adding something to the blobstore

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


def property_not_none_key_value_pair_with_permissions(class_reference):
    if class_reference is not None and class_reference.permissions is not None:
        permissions = class_reference.permissions[class_reference.class_name]
        return property_not_none_key_value_pair(class_reference, permissions)


def property_not_none_key_value_pair(class_reference, prop_list):
        return_data = {}
        if prop_list is not None:
            for prop in prop_list:
                value = getattr(class_reference, prop)
                if value is not None:
                    try:
                        if isinstance(value, collections.MutableSequence):
                            temp = list()
                            for key in value:
                                try:
                                    temp.append(key.integer_id())
                                except AttributeError:
                                    continue
                            value = temp
                        else:
                            value = value.integer_id()
                    except AttributeError:
                        value = str(value)
                    return_data = dict(return_data.items() + {prop: value}.items())
        return return_data

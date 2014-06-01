__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import json
import collections

# Department Model class
class Department(ndb.Model):
    name = ndb.StringProperty()

    def get_object_as_data_dict(self):
        return {'id': self.key.integer_id(),
                'name': self.name}


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
    max_declaration_price = ndb.IntegerProperty()

    all_custom_properties = ["first_name", "last_name", "email", "employee_number",
                             "supervisor", "max_declaration_price"]
    permissions = {"user": ["first_name", "last_name", "email", "class_name"],
                   "employee": ["first_name", "last_name", "email", "employee_number",
                                "supervisor", "class_name"],
                   "supervisor": ["first_name", "last_name", "email", "employee_number",
                                  "supervisor", "class_name", "max_declaration_price"],
                   "human_resources": ["first_name", "last_name", "email", "employee_number",
                                       "supervisor"]}

    def get_object_as_data_dict(self):
        department = Department.get_by_id(self.department.integer_id())

        return dict({'id': self.key.integer_id(),
                     'class_name': self.class_name,
                     'department': department.get_object_as_data_dict()}.items() +
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
    lines = ndb.KeyProperty(kind="DeclarationLine", repeated=True)
    attachments = ndb.KeyProperty(kind="Attachment", repeated=True)
    comment = ndb.StringProperty()
    items_count = ndb.IntegerProperty()
    items_total_price = ndb.IntegerProperty()
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
    all_custom_properties = ["created_at", "assigned_to", "comment", "items_total_price", "items_count"
                             "supervisor_comment", "human_resources_comment", "declined_by",
                             "submitted_to_human_resources_by", "locked_at", "sent_to_human_resources_at",
                             "supervisor_declined_at", "supervisor_approved_at", "human_resources_approved_at",
                             "human_resources_declined_at", "will_be_payed_out_on", "human_resources_approved_by"]

    permissions = {"open_declaration": ["created_at", "assigned_to", "comment", "items_total_price",
                                        "items_count"],

                   "locked_declaration": ["created_at", "assigned_to", "comment", "items_total_price",
                                          "items_count", "locked_at", "supervisor_comment"],

                   "supervisor_declined_declaration": ["created_at", "assigned_to", "comment",
                                                       "items_total_price", "items_count", "locked_at", "declined_by",
                                                       "supervisor_declined_at", "supervisor_comment"],

                   "supervisor_approved_declaration": ["created_at", "assigned_to", "comment",
                                                       "items_total_price", "items_count", "locked_at",
                                                       "submitted_to_human_resources_by", "supervisor_approved_at",
                                                       "supervisor_approved_by", "sent_to_human_resources_at",
                                                       "supervisor_comment"],

                   "human_resources_declined_declaration": ["created_at", "assigned_to", "comment",
                                                            "items_total_price", "items_count", "locked_at",
                                                            "submitted_to_human_resources_by", "supervisor_approved_at",
                                                            "supervisor_approved_by", "sent_to_human_resources_at",
                                                            "declined_by", "supervisor_comment",
                                                            "human_resources_comment", "human_resources_declined_at",
                                                            "human_resources_declined_by"],

                   "human_resources_approved_declaration": ["created_at", "assigned_to", "comment",
                                                            "items_total_price", "items_count", "locked_at",
                                                            "submitted_to_human_resources_by", "supervisor_approved_at",
                                                            "supervisor_approved_by", "sent_to_human_resources_at",
                                                            "supervisor_comment", "will_be_payed_out_on",
                                                            "human_resources_comment", "human_resources_approved_by",
                                                            "human_resources_approved_at"]}

    def get_last_assigned_to(self):
        return self.assigned_to[len(self.assigned_to)-1]

    def get_object_as_data_dict(self):
        owner = Person.get_by_id(self.created_by.integer_id())

        return dict({'id': self.key.integer_id(),
                     'class_name': self.class_name,
                     "state": self.readable_state(),
                     "created_by": owner.get_object_as_data_dict()}.items() +
                    property_not_none_key_value_pair_with_permissions(self).items())

    def get_object_as_full_data_dict(self):
        last_assigned_to = Person.get_by_id(self.get_last_assigned_to().integer_id())
        owner = Person.get_by_id(self.created_by.integer_id())

        declaration_lines = []
        if len(self.lines) > 0:
            declaration_lines = DeclarationLine.query(DeclarationLine.key.IN(self.lines)).fetch()

        attachments = []
        if len(self.attachments) > 0:
            attachments = Attachment.query(Attachment.key.IN(self.attachments)).fetch()

        return dict({'id': self.key.integer_id(),
                     'class_name': self.class_name,
                     'last_assigned_to': last_assigned_to.get_object_as_data_dict(),
                     "state": self.readable_state(),
                     "lines": map(lambda declaration_item: declaration_item.get_object_as_full_data_dict(), declaration_lines),
                     "attachments": map(lambda attachment: attachment.get_object_as_data_dict(), attachments),
                     "created_by": owner.get_object_as_data_dict()
                     }.items() +
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
    declaration_type = ndb.KeyProperty(kind="DeclarationType")
    max_cost = ndb.IntegerProperty()  # Optional

    all_custom_properties = ['name', 'max_cost', 'declaration_type']

    def get_object_as_data_dict(self):
        return dict({'id': self.key.integer_id()}.items() + property_not_none_key_value_pair(self, self.all_custom_properties).items())

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


# DeclarationType Model class
class DeclarationType(ndb.Model):
    name = ndb.StringProperty()
    sub_types = ndb.KeyProperty(kind="DeclarationSubType", repeated=True)

    all_custom_properties = ['name', 'sub_types']

    def get_object_as_data_dict(self):
        return dict({'id': self.key.integer_id()}.items() + property_not_none_key_value_pair(self, self.all_custom_properties).items())

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


# DeclarationLine Model class
class DeclarationLine(ndb.Model):
    receipt_date = ndb.DateTimeProperty()
    cost = ndb.IntegerProperty()
    declaration_sub_type = ndb.KeyProperty(kind=DeclarationSubType)
    comment = ndb.StringProperty()

    all_custom_properties = ['receipt_date', 'cost', 'declaration_sub_type', 'comment']

    def get_object_as_data_dict(self):
        return dict({'id': self.key.integer_id()}.items() + property_not_none_key_value_pair(self, self.all_custom_properties).items())

    def get_object_as_full_data_dict(self):
        subdeclaration = DeclarationSubType.get_by_id(self.declaration_sub_type.integer_id())
        declaration = DeclarationType.get_by_id(subdeclaration.declaration_type.integer_id())

        return dict({'id': self.key.integer_id(),
                     'cost': self.cost,
                     'receipt_date': str(self.receipt_date),
                     'comment': self.comment,
                     'declaration_sub_type': subdeclaration.get_object_as_data_dict(),
                     'declaration_type': declaration.get_object_as_data_dict()}.items())

    def get_object_json_data(self):
        return json.dumps(self.get_object_as_data_dict())


class Attachment(ndb.Model):
    declaration = ndb.KeyProperty(kind=Declaration)
    name = ndb.StringProperty()
    token = ndb.StringProperty()
    file = ndb.TextProperty()

    def get_object_as_full_data_dict(self):
        return dict({'id': self.key.integer_id(), 'declaration_id': self.declaration.integer_id(), 'name': self.name, 'file': self.file})

    def get_object_as_data_dict(self):
        return dict({'id': self.key.integer_id(), 'declaration_id': self.declaration.integer_id(), 'name': self.name})

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

__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from google.appengine.ext import blobstore


# Department Model class
class Department(ndb.Model):
    name = ndb.StringProperty

    def details(self):
        return {'name': self.name}


# Person Model class
class User(polymodel.PolyModel):
    class_name = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    employee_number = ndb.IntegerProperty()
    department = ndb.KeyProperty(kind=Department)
    supervisor = ndb.KeyProperty(kind="User")

    def details(self):
        return {'id': self.key.integer_id(),
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'employee_number': self.employee_number}
        #        'department': self.department.id(),
        #        'supervisor': self.supervisor.id()}

    @classmethod
    def _get_kind(cls):
        return "User"  # TODO

    def __setattr__(self, key, value):
        all_custom_properties = ["first_name", "last_name", "email", "employee_number", "department",
                                 "supervisor"]
        if key in all_custom_properties:
            permissions = {"user": ["first_name", "last_name", "email"],
                           "employee": ["first_name", "last_name", "email", "employee_number", "department",
                                        "supervisor"],
                           "supervisor": ["first_name", "last_name", "email", "employee_number", "department",
                                          "supervisor"],
                           "human_resources": ["first_name", "last_name", "email", "employee_number", "department",
                                               "supervisor"]}
            object.__setattr__(self, key, self.handle_custom_property_set_operation(permissions, key, value))
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
    created_by = ndb.KeyProperty(kind=User)
    assigned_to = ndb.KeyProperty(kind=User)
    comment = ndb.StringProperty()
    declined_by = ndb.KeyProperty(kind=User)
    submitted_to_hr_by = ndb.KeyProperty(kind=User)
    approved_by = ndb.KeyProperty(kind=User)

    def details(self):
        return {'id': self.key().id(),
                'created_at': str(self.created_at),
                'created_by': self.created_by.integer_id(),
                'assigned_to': self.assigned_to.integer_id(),
                'comment': self.comment,
                'declined_by': self.declined_by.integer_id(),
                'submitted_to_hr_by': self.submitted_to_hr_by.integer_id(),
                'approved_by': self.approved_by.integer_id()}

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
        all_custom_properties = ["created_at", "created_by", "assigned_to", "comment", "declined_by",
                                 "submitted_to_hr_by"]
        if key in all_custom_properties:
            permissions = {"open_declaration": ["created_at", "created_by", "assigned_to", "comment"],
                           "closed_declaration": ["created_at", "created_by", "assigned_to", "comment", "declined_by",
                                                  "submitted_to_hr_by"],
                           "declined_declaration": ["created_at", "created_by", "assigned_to", "comment", "declined_by",
                                                    "submitted_to_hr_by"],
                           "approved_declaration": ["created_at", "created_by", "assigned_to", "comment", "declined_by",
                                                    "submitted_to_hr_by"]}

            object.__setattr__(self, key, self.handle_custom_property_set_operation(permissions, key, value))
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


# DeclarationType Model class
class DeclarationType(ndb.Model):
    declaration_sub_types = ndb.KeyProperty(kind=DeclarationSubType)

    def details(self):
        return {'declaration_sub_types': self.declaration_sub_types.integer_id()}


# DeclarationLine Model class
class DeclarationLine(ndb.Model):
    receipt_date = ndb.StringProperty()  # DateProperty?
    cost = ndb.IntegerProperty()
    declaration_type = ndb.KeyProperty(kind=DeclarationType)
    declaration_sub_type = ndb.KeyProperty(kind=DeclarationSubType)

    def details(self):
        return {'receipt_date': self.receipt_date,
                'cost': self.cost,
                'declaration_type': self.declaration_type.integer_id(),
                'declaration_sub_type': self.declaration_sub_type.integer_id()}


class Attachment(ndb.Model):
    ndb.KeyProperty(kind=Declaration)
    blobstore.BlobReferenceProperty(required=True)

    def details(self):
        return {'': ""}  # TODO details
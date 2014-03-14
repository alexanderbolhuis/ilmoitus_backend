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


# OpenDeclaration Model class
class Declaration(polymodel.PolyModel):
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

    @property
    def id(self):
        return self.key.integer_id()


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
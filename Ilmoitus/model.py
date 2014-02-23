__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from google.appengine.ext import blobstore


# Person Model class
class Person(polymodel.PolyModel):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()


# Department Model class
class Department(ndb.Model):
    name = ndb.StringProperty


# Employee Model class
class Employee(Person):
    employee_number = ndb.IntegerProperty()
    department = ndb.KeyProperty(kind=Department)
    supervisor = ndb.KeyProperty(kind="Supervisor")

    @classmethod
    def _get_kind(cls):
        return "Employee"


# AdministrativeEmployee Model class
class AdministrativeEmployee(Employee):
    @classmethod
    def _get_kind(cls):
        return "AdministrativeEmployee"


# HumanResources Model class
class HumanResources(AdministrativeEmployee):
    @classmethod
    def _get_kind(cls):
        return "HumanResources"


# Supervisor Model class
class Supervisor(AdministrativeEmployee):
    @classmethod
    def _get_kind(cls):
        return "Supervisor"


# OpenDeclaration Model class
class OpenDeclaration(polymodel.PolyModel):
    created_at = ndb.StringProperty()  # DateProperty?
    created_by = ndb.KeyProperty(kind=Employee)
    assigned_to = ndb.KeyProperty(kind=Supervisor)
    comment = ndb.StringProperty()

    def details(self):
        return {'id': self.key().id(),
                'created_at': self.created_at,
                'created_by': self.created_by,
                'assigned_to': self.assigned_to,
                'comment': self.comment}


# LockedDeclaration Model class
class LockedDeclaration(OpenDeclaration):
    assigned_to = ndb.KeyProperty(kind=Supervisor)

    def details(self):
        super_dict = super(LockedDeclaration, self).details()
        self_dict = {'assigned_to': self.assigned_to}
        return dict(super_dict.items() + self_dict.items())


# DeclinedDeclaration Model class
class DeclinedDeclaration(LockedDeclaration):
    declined_by = ndb.KeyProperty(kind=AdministrativeEmployee)

    def details(self):
        super_dict = super(DeclinedDeclaration, self).details()
        self_dict = {'declined_by': self.declined_by}
        return dict(super_dict.items() + self_dict.items())


# SuperVisorApprovedDeclaration Model class
class SuperVisorApprovedDeclaration(LockedDeclaration):
    submitted_to_hr_by = ndb.KeyProperty(kind=Supervisor)

    def details(self):
        super_dict = super(SuperVisorApprovedDeclaration, self).details()
        self_dict = {'submitted_to_hr_by': self.submitted_to_hr_by}
        return dict(super_dict.items() + self_dict.items())


# CompletelyApprovedDeclaration Model class
class CompletelyApprovedDeclaration(SuperVisorApprovedDeclaration):
    approved_by = ndb.KeyProperty(kind=HumanResources)

    def details(self):
        super_dict = super(CompletelyApprovedDeclaration, self).details()
        self_dict = {'approved_by': self.approved_by}
        return dict(super_dict.items() + self_dict.items())


# DeclarationSubType Model class
class DeclarationSubType(ndb.Model):
    name = ndb.StringProperty()
    max_cost = ndb.IntegerProperty()  # Optional


# DeclarationType Model class
class DeclarationType(ndb.Model):
    declaration_sub_types = ndb.KeyProperty(kind=DeclarationSubType)

    def details(self):
        return {'declaration_sub_types': self.declaration_sub_types}


# DeclarationLine Model class
class DeclarationLine(ndb.Model):
    receipt_date = ndb.StringProperty()  # DateProperty?
    cost = ndb.IntegerProperty()
    declaration_type = ndb.KeyProperty(kind=DeclarationType)
    declaration_sub_type = ndb.KeyProperty(kind=DeclarationSubType)

    def details(self):
        return {'receipt_date': self.receipt_date,
                'cost': self.cost,
                'declaration_type': self.declaration_type,
                'declaration_sub_type': self.declaration_sub_type}


class Attachment(ndb.Model):
    ndb.KeyProperty(kind=OpenDeclaration)
    blobstore.BlobReferenceProperty(required=True)
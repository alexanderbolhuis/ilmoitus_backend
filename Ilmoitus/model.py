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


# AdministrativeEmployee Modelclass
class AdministrativeEmployee(Employee):
    @classmethod
    def _get_kind(cls):
        return "AdministrativeEmployee"


# HumanResources Modelclass
class HumanResources(AdministrativeEmployee):
    @classmethod
    def _get_kind(cls):
        return "HumanResources"


# Supervisor Modelclass
class Supervisor(AdministrativeEmployee):
    @classmethod
    def _get_kind(cls):
        return "Supervisor"


# OpenDeclaration Modelclass
class OpenDeclaration(polymodel.PolyModel):
    created_at = ndb.StringProperty()  # DateProperty?
    created_by = ndb.KeyProperty(kind=Employee)
    assigned_to = ndb.KeyProperty(kind=Supervisor)
    comment = ndb.StringProperty()


# LockedDeclaration Modelclass
class LockedDeclaration(OpenDeclaration):
    assigned_to = ndb.KeyProperty(kind=Supervisor)


# DeclinedDeclaration Modelclass
class DeclinedDeclaration(LockedDeclaration):
    declined_by = ndb.KeyProperty(kind=AdministrativeEmployee)


# SuperVisorApprovedDeclaration Modelclass
class SuperVisorApprovedDeclaration(LockedDeclaration):
    submitted_to_hr_by = ndb.KeyProperty(kind=Supervisor)


# CompletelyApprovedDeclaration Modelclass
class CompletelyApprovedDeclaration(SuperVisorApprovedDeclaration):
    approved_by = ndb.KeyProperty(kind=HumanResources)


# DeclarationSubType Modelclass
class DeclarationSubType(ndb.Model):
    name = ndb.StringProperty()
    max_cost = ndb.IntegerProperty()  # Optional


# DeclarationType Modelclass
class DeclarationType(ndb.Model):
    declaration_sub_types = ndb.KeyProperty(kind=DeclarationSubType)


# DeclarationLine Modelclass
class DeclarationLine(ndb.Model):
    receipt_date = ndb.StringProperty()  # DateProperty?
    cost = ndb.IntegerProperty()
    declaration_type = ndb.KeyProperty(kind=DeclarationType)
    declaration_sub_type = ndb.KeyProperty(kind=DeclarationSubType)


class Attachment(ndb.Model):
    ndb.KeyProperty(kind=OpenDeclaration)
    blobstore.BlobReferenceProperty(required=True)
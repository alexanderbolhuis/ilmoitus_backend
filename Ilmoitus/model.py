__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from google.appengine.ext import blobstore


# Person Modelclass
class Person(polymodel.PolyModel):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()


# Department Modelclass
class Department(ndb.Model):
    name = ndb.StringProperty
    f

# Employee Modelclass
class Employee(Person):
    employee_number = ndb.IntegerProperty()
    department = ndb.KeyProperty(kind=Department)
    supervisor = ndb.KeyProperty(kind=Supervisor)


# AdministrativeEmployee Modelclass
class AdministrativeEmployee(Employee):
    pass


# HumanResources Modelclass
class HumanResources(AdministrativeEmployee):
    pass


# Supervisor Modelclass
class Supervisor(AdministrativeEmployee):
    pass


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


# DeclarationLine Modelclass
class DeclarationLine(ndb.Model):
    receipt_date = ndb.StringProperty()  # DateProperty?
    cost = ndb.IntegerProperty()
    declaration_type = ndb.KeyProperty(kind=DeclarationType)
    declaration_sub_type = ndb.KeyProperty(kind=DeclarationSubType)


# DeclarationType Modelclass
class DeclarationType(ndb.Model):
    declaration_sub_types = ndb.KeyProperty(kind=DeclarationSubType)


# DeclarationSubType Modelclass
class DeclarationSubType(ndb.Model):
    name = ndb.StringProperty()
    max_cost = ndb.IntegerProperty()  # Optional


class Attachment(ndb.Model):
    ndb.KeyProperty(kind=OpenDeclaration)
    blobstore.BlobReferenceProperty(required=True)
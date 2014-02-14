__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

# Person Modelclass
class Person(polymodel.Polymodel):
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    email = db.StringProperty()

# Employee Modelclass
class Employee(Person):
    employee_number = db.IntegerProperty()
    department = db.ReferenceProperty(Department)
    supervisor = db.ReferenceProperty(Supervisor)

# AdministrativeEmployee Modelclass
class AdministrativeEmployee(Employee):
    def temp(self):
        return True

# HumanResources Modelclass
class HumanResources(AdministrativeEmployee):
    def temp(self):
        return True

# Supervisor Modelclass
class Supervisor(AdministrativeEmployee):
    def temp(self):
        return True

# Department Modelclass
class Department(db.Model):
    name = db.StringProperty

# OpenDeclaration Modelclass
class OpenDeclaration(polymodel.Polymodel):
    created_at = db.StringProperty() # DateProperty?
    created_by = db.ReferenceProperty(Employee)
    assigned_to = db.ReferenceProperty(Supervisor)

# LockedDeclaration Modelclass
class LockedDeclaration(OpenDeclaration):
    assigned_to = db.ReferenceProperty(Supervisor, collection_name="assignedTo")

# DeclinedDeclaration Modelclass
class DeclinedDeclaration(LockedDeclaration):
    declined_by = db.ReferenceProperty(AdministrativeEmployee)

# SuperVisorApprovedDeclaration Modelclass
class SuperVisorApprovedDeclaration(LockedDeclaration):
    submitted_to_hr_by = db.ReferenceProperty(Supervisor)

# CompletelyApprovedDeclaration Modelclass
class CompletelyApprovedDeclaration(SuperVisorApprovedDeclaration):
    approved_by = db.ReferenceProperty(HumanResources)

# DeclarationLine Modelclass
class DeclarationLine(db.Model):
    receipt_date = db.StringProperty() # DateProperty?
    cost = db.IntegerProperty()
    declaration_type = db.ReferenceProperty(DeclarationType)
    declaration_sub_type = db.ReferenceProperty(DeclarationSubType)

# DeclarationType Modelclass
class DeclarationType(db.Model):
    declaration_sub_types = db.ReferenceProperty(DeclarationSubType, collection_name="declarationSubTypes")

# DeclarationSubType Modelclass
class DeclarationSubType(db.Model):
    name = db.StringProperty()
    max_cost = db.IntegerProperty() # Optional

class Attachment(db.Model):
    declaration = db.ReferenceProperty(OpenDeclaration)
    # Blob?
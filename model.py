__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

# Person Modelclass
class Person(polymodel.Polymodel):
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    email = db.StringProperty()

    def details(self):
        return {'id': self.key().id(),
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email}

# Employee Modelclass
class Employee(Person):
    employee_number = db.IntegerProperty()
    department = db.ReferenceProperty(Department)
    supervisor = db.ReferenceProperty(Supervisor)

    def details(self):
        super_dict = super(Person, self).details()
        self_dict = {'employee_number': self.employee_number,
                     'department': self.department,
                     'supervisor': self.supervisor}
        return dict(super_dict.items() + self_dict.items())

# AdministrativeEmployee Modelclass
class AdministrativeEmployee(Employee):
    def details(self):
        super_dict = super(Employee, self).details()
        return dict(super_dict.items())

# HumanResources Modelclass
class HumanResources(AdministrativeEmployee):
    def details(self):
        super_dict = super(AdministrativeEmployee, self).details()
        return dict(super_dict.items())

# Supervisor Modelclass
class Supervisor(AdministrativeEmployee):
    def details(self):
        super_dict = super(AdministrativeEmployee, self).details()
        return dict(super_dict.items())

# Department Modelclass
class Department(db.Model):
    name = db.StringProperty

    def details(self):
        return {'name': self.name}

# OpenDeclaration Modelclass
class OpenDeclaration(polymodel.Polymodel):
    created_at = db.StringProperty() # DateProperty?
    created_by = db.ReferenceProperty(Employee)
    assigned_to = db.ReferenceProperty(Supervisor)
    comment = db.StringProperty()

# LockedDeclaration Modelclass
class LockedDeclaration(OpenDeclaration):
    assigned_to = db.ReferenceProperty(Supervisor)

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
    declaration_sub_types = db.ReferenceProperty(DeclarationSubType)

# DeclarationSubType Modelclass
class DeclarationSubType(db.Model):
    name = db.StringProperty()
    max_cost = db.IntegerProperty() # Optional

class Attachment(db.Model):
    db.ReferenceProperty(OpenDeclaration)
    blobstore.BlobReferenceProperty(required=True)

    def details(self):
        # blobstore?
        super_dict = super(Person, self).details()
        return dict(super_dict.items())
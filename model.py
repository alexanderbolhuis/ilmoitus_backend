__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import db
from google.appengine.ext.db import polymodel


# Person ModelClass
class Person(polymodel.Polymodel):
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    email = db.StringProperty()


# Employee ModelClass
class Employee(Person):
    employee_number = db.IntegerProperty()
    department = db.ReferenceProperty(Department)
    supervisor = db.ReferenceProperty(Supervisor)


# AdministrativeEmployee ModelClass
class AdministrativeEmployee(Employee):
    pass


# HumanResources ModelClass
class HumanResources(AdministrativeEmployee):
    pass


# Supervisor ModelClass
class Supervisor(AdministrativeEmployee):
    pass


# Department ModelClass
class Department(db.Model):
    name = db.StringProperty


# OpenDeclaration ModelClass
class OpenDeclaration(polymodel.Polymodel):
    created_at = db.StringProperty()  # DateProperty?
    created_by = db.ReferenceProperty(Employee)
    assigned_to = db.ReferenceProperty(Supervisor)
    comment = db.StringProperty()

    def details(self):
        return {'id': self.key().id(),
                'created_at': self.created_at,
                'created_by': self.created_by,
                'assigned_to': self.assigned_to,
                'comment': self.comment}


# LockedDeclaration ModelClass
class LockedDeclaration(OpenDeclaration):
    assigned_to = db.ReferenceProperty(Supervisor)

    def details(self):
        super_dict = super(LockedDeclaration, self).details()
        self_dict = {'assigned_to': self.assigned_to}
        return dict(super_dict.items() + self_dict.items())


# DeclinedDeclaration ModelClass
class DeclinedDeclaration(LockedDeclaration):
    declined_by = db.ReferenceProperty(AdministrativeEmployee)

    def details(self):
        super_dict = super(DeclinedDeclaration, self).details()
        self_dict = {'declined_by': self.declined_by}
        return dict(super_dict.items() + self_dict.items())


# SuperVisorApprovedDeclaration ModelClass
class SuperVisorApprovedDeclaration(LockedDeclaration):
    submitted_to_hr_by = db.ReferenceProperty(Supervisor)

    def details(self):
        super_dict = super(SuperVisorApprovedDeclaration, self).details()
        self_dict = {'submitted_to_hr_by': self.submitted_to_hr_by}
        return dict(super_dict.items() + self_dict.items())


# CompletelyApprovedDeclaration ModelClass
class CompletelyApprovedDeclaration(SuperVisorApprovedDeclaration):
    approved_by = db.ReferenceProperty(HumanResources)

    def details(self):
        super_dict = super(CompletelyApprovedDeclaration, self).details()
        self_dict = {'approved_by': self.approved_by}
        return dict(super_dict.items() + self_dict.items())


# DeclarationLine ModelClass
class DeclarationLine(db.Model):
    receipt_date = db.StringProperty()  # DateProperty?
    cost = db.IntegerProperty()
    declaration_type = db.ReferenceProperty(DeclarationType)
    declaration_sub_type = db.ReferenceProperty(DeclarationSubType)

    def details(self):
        return {'receipt_date': self.receipt_date,
                'cost': self.cost,
                'declaration_type': self.declaration_type,
                'declaration_sub_type': self.declaration_sub_type}


# DeclarationType ModelClass
class DeclarationType(db.Model):
    declaration_sub_types = db.ReferenceProperty(DeclarationSubType)

    def details(self):
        return {'declaration_sub_types': self.declaration_sub_types}


# DeclarationSubType ModelClass
class DeclarationSubType(db.Model):
    name = db.StringProperty()
    max_cost = db.IntegerProperty()  # Optional

    def details(self):
        return {'name': self.name,
                'max_cost': self.max_cost}


class Attachment(db.Model):
    db.ReferenceProperty(OpenDeclaration)
    blobstore.BlobReferenceProperty(required=True)
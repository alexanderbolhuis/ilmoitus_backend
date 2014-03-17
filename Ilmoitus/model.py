__author__ = 'alexanderbolhuis & sjorsboom'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from google.appengine.ext import blobstore


# Person Model class
class Person(polymodel.PolyModel):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    wants_email_notifications = ndb.BooleanProperty()
    wants_phone_notifications = ndb.BooleanProperty()

    def details(self):
        return {'id': self.key.integer_id(),
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'wants_email_notifications': self.wants_email_notifications,
                'wants_phone_notifications': self.wants_phone_notifications}

    def settings(self):
        return {'wants_email_notifications': self.wants_email_notifications,
                'wants_phone_notifications': self.wants_phone_notifications}


# Department Model class
class Department(ndb.Model):
    name = ndb.StringProperty

    def details(self):
        return {'name': self.name}


# Employee Model class
class Employee(Person):
    employee_number = ndb.IntegerProperty()
    department = ndb.KeyProperty(kind=Department)
    supervisor = ndb.KeyProperty(kind="Supervisor")

    @classmethod
    def _get_kind(cls):
        return "Employee"

    def details(self):
        super_obj = super(Employee, self)
        super_dict = super_obj.details()
        self_dict = {'employee_number': self.employee_number,
                     'department': self.department.integer_id(),
                     'supervisor': self.supervisor.integer_id()}
        return dict(super_dict.items() + self_dict.items())


# AdministrativeEmployee Model class
class AdministrativeEmployee(Employee):
    @classmethod
    def _get_kind(cls):
        return "AdministrativeEmployee"

    def details(self):
        super_dict = super(AdministrativeEmployee, self).details()
        return dict(super_dict.items())


# HumanResources Model class
class HumanResources(AdministrativeEmployee):
    @classmethod
    def _get_kind(cls):
        return "HumanResources"

    def details(self):
        super_dict = super(HumanResources, self).details()
        return dict(super_dict.items())


# Supervisor Model class
class Supervisor(AdministrativeEmployee):
    @classmethod
    def _get_kind(cls):
        return "Supervisor"

    def details(self):
        super_dict = super(Supervisor, self).details()
        return dict(super_dict.items())


# OpenDeclaration Model class
class OpenDeclaration(polymodel.PolyModel):
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    created_by = ndb.KeyProperty(kind=Employee)
    assigned_to = ndb.KeyProperty(kind=Supervisor)
    comment = ndb.StringProperty()

    def details(self):
        return {'id': self.key().id(),
                'created_at': str(self.created_at),
                'created_by': self.created_by.integer_id(),
                'assigned_to': self.assigned_to.integer_id(),
                'comment': self.comment}


# LockedDeclaration Model class
class LockedDeclaration(OpenDeclaration):
    assigned_to = ndb.KeyProperty(kind=Supervisor)

    def details(self):
        super_dict = super(LockedDeclaration, self).details()
        self_dict = {'assigned_to': self.assigned_to.integer_id()}
        return dict(super_dict.items() + self_dict.items())


# DeclinedDeclaration Model class
class DeclinedDeclaration(LockedDeclaration):
    declined_by = ndb.KeyProperty(kind=AdministrativeEmployee)

    def details(self):
        super_dict = super(DeclinedDeclaration, self).details()
        self_dict = {'declined_by': self.declined_by.integer_id()}
        return dict(super_dict.items() + self_dict.items())


# SuperVisorApprovedDeclaration Model class
class SuperVisorApprovedDeclaration(LockedDeclaration):
    submitted_to_hr_by = ndb.KeyProperty(kind=Supervisor)

    def details(self):
        super_dict = super(SuperVisorApprovedDeclaration, self).details()
        self_dict = {'submitted_to_hr_by': self.submitted_to_hr_by.integer_id()}
        return dict(super_dict.items() + self_dict.items())


# CompletelyApprovedDeclaration Model class
class CompletelyApprovedDeclaration(SuperVisorApprovedDeclaration):
    approved_by = ndb.KeyProperty(kind=HumanResources)

    def details(self):
        super_dict = super(CompletelyApprovedDeclaration, self).details()
        self_dict = {'approved_by': self.approved_by.integer_id()}
        return dict(super_dict.items() + self_dict.items())


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
    ndb.KeyProperty(kind=OpenDeclaration)
    blobstore.BlobReferenceProperty(required=True)

    def details(self):
        return {'': ""}  # TODO details

__author__ = 'niek'

import webapp2
import ilmoitus_model
from google.appengine.ext import ndb
import urllib

class DataBootsTrapper(webapp2.RequestHandler):
    def create_data(self):
        #DEPARTMENTS

        department_it = ilmoitus_model.Department()
        department_it.name = "IT"
        department_it.put()

        department_investment = ilmoitus_model.Department()
        department_investment.name = "Investment"
        department_investment.put()

        #SUPERVISORS

        supervisor_one = ilmoitus_model.User()
        supervisor_one.class_name = "supervisor"
        supervisor_one.first_name = "Wim"
        supervisor_one.last_name = "Meredonk"
        supervisor_one.email = "Willem_Naaktloper@gmail.com"
        supervisor_one.employee_number = 1
        supervisor_one.department = department_it.key
        supervisor_one.supervisor = None
        supervisor_one.put()


        supervisor_two = ilmoitus_model.User()
        supervisor_two.class_name = "supervisor"
        supervisor_two.first_name = "Muhammad"
        supervisor_two.last_name = "Hasdim"
        supervisor_two.email = "Muhammad_Hasdim@gmail.com"
        supervisor_two.employee_number = 4
        supervisor_two.department = department_it.key
        supervisor_two.supervisor = supervisor_one.key
        supervisor_two.put()

        supervisor_three = ilmoitus_model.User()
        supervisor_three.class_name = "supervisor"
        supervisor_three.first_name = "Wout"
        supervisor_three.last_name = "van Diesen"
        supervisor_three.email = "Wout_van_Diesen@gmail.com"
        supervisor_three.employee_number = 7
        supervisor_three.department = department_investment.key
        supervisor_three.supervisor = None
        supervisor_three.put()

        #EMPLOYEES
        employee_one = ilmoitus_model.User()
        employee_one.class_name = "employee"
        employee_one.first_name = "Piet"
        employee_one.last_name = "Hein"
        employee_one.email = "Piet_Hein@gmail.com"
        employee_one.employee_number = 2
        employee_one.department = department_it.key
        employee_one.supervisor = supervisor_one.key
        employee_one.put()

        employee_two = ilmoitus_model.User()
        employee_two.class_name = "employee"
        employee_two.first_name = "Axel"
        employee_two.last_name = "Klein"
        employee_two.email = "Axel_Klein@gmail.com"
        employee_two.employee_number = 3
        employee_two.department = department_it.key
        employee_two.supervisor = supervisor_one.key
        employee_two.put()

        employee_three = ilmoitus_model.User()
        employee_three.class_name = "employee"
        employee_three.first_name = "Rik"
        employee_three.last_name = "van de Griendt"
        employee_three.email = "Rik_Kleinlul@gmail.com"
        employee_three.employee_number = 5
        employee_three.department = department_it.key
        employee_three.supervisor = supervisor_two.key
        employee_three.put()

        employee_five = ilmoitus_model.User()
        employee_five.class_name = "human_resources"
        employee_five.first_name = "Laura"
        employee_five.last_name = "Vermeulen"
        employee_five.email = "Laura_Vermeulen@gmail.com"
        employee_five.employee_number = 9
        employee_five.department = department_investment.key
        employee_five.supervisor = supervisor_three.key
        employee_five.put()

        #DECLARATIE
        declaratie_een = ilmoitus_model.Declaration()
        declaratie_een.class_name = "open_declaration"
        declaratie_een.created_by = employee_one.key
        declaratie_een.assigned_to = employee_one.supervisor
        declaratie_een.comment = "Gegeten op zakenreis"
        declaratie_een.put()

        declaratie_two = ilmoitus_model.Declaration()
        declaratie_two.class_name = "open_declaration"
        declaratie_two.created_by = employee_one.key
        declaratie_two.assigned_to = employee_one.supervisor
        declaratie_two.comment = "Tanken op zakenreis"
        declaratie_two.put()

        declaratie_three = ilmoitus_model.Declaration()
        declaratie_three.class_name = "open_declaration"
        declaratie_three.created_by = employee_one.key
        declaratie_three.assigned_to = employee_one.supervisor
        declaratie_three.comment = "Parkeren voor de vergadering met de rabobank"
        declaratie_three.put()

        declaratie_four = ilmoitus_model.Declaration()
        declaratie_four.class_name = "open_declaration"
        declaratie_four.created_by = employee_two.key
        declaratie_four.assigned_to = employee_two.supervisor
        declaratie_four.comment = "Vlucht kosten zakenreis naar engeland"
        declaratie_four.put()

        declaratie_five = ilmoitus_model.Declaration()
        declaratie_five.class_name = "supervisor_declined_declaration"
        declaratie_five.created_by = employee_two.key
        declaratie_five.assigned_to = employee_two.supervisor
        declaratie_five.comment = "Bedrijfsuitje"
        declaratie_five.declined_by = employee_two.supervisor
        declaratie_five.submitted_to_hr_by = employee_two.supervisor
        declaratie_five.put()


class ClearHandler(webapp2.RequestHandler):
    def clear_data(self):
        for department in ilmoitus_model.Department.query():
            department.key.delete()
        for user in ilmoitus_model.User.query():
            user.key.delete()
        for declaration in ilmoitus_model.Declaration.query():
            declaration.key.delete()

    def get(self):
        self.clear_data()


class CreateDataHandler(webapp2.RequestHandler):
    def get(self):
        data = DataBootsTrapper()
        data.create_data()


class FillHandler(webapp2.RequestHandler):
    def get(self):
        clearer = ClearHandler()
        clearer.clear_data()

        data = DataBootsTrapper()
        data.create_data()
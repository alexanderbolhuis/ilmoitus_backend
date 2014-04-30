__author__ = 'niek'

import webapp2
import ilmoitus_model
import datetime
import ilmoitus_auth

class DataBootsTrapper(webapp2.RequestHandler):
    @staticmethod
    def create_data():
        #DEPARTMENTS

        department_it = ilmoitus_model.Department()
        department_it.name = "IT"
        department_it.put()

        department_investment = ilmoitus_model.Department()
        department_investment.name = "Investment"
        department_investment.put()

        department_human_resources = ilmoitus_model.Department()
        department_human_resources.name = "P&O"
        department_human_resources.put()

        #SUPERVISORS
        supervisor_one = ilmoitus_model.Person()
        supervisor_one.class_name = "supervisor"
        supervisor_one.first_name = "Wim"
        supervisor_one.last_name = "Meredonk"
        supervisor_one.email = "wjm.meredonk1@gmail.com"
        supervisor_one.password = ilmoitus_auth.hash_secret("123456")
        supervisor_one.employee_number = 1
        supervisor_one.department = department_it.key
        supervisor_one.supervisor = None
        supervisor_one.put()

        supervisor_two = ilmoitus_model.Person()
        supervisor_two.class_name = "supervisor"
        supervisor_two.first_name = "Muhammed"
        supervisor_two.last_name = "Hasdim"
        supervisor_two.email = "muhammad_hasdim@gmail.com"
        supervisor_two.password = ilmoitus_auth.hash_secret("123456")
        supervisor_two.employee_number = 4
        supervisor_two.department = department_it.key
        supervisor_two.supervisor = supervisor_one.key
        supervisor_two.put()

        supervisor_three = ilmoitus_model.Person()
        supervisor_three.class_name = "supervisor"
        supervisor_three.first_name = "Wout"
        supervisor_three.last_name = "van Diesen"
        supervisor_three.email = "wout_van_diesen@gmail.com"
        supervisor_three.password = ilmoitus_auth.hash_secret("123456")
        supervisor_three.employee_number = 7
        supervisor_three.department = department_investment.key
        supervisor_three.supervisor = None
        supervisor_three.put()

        #EMPLOYEES
        employee_one = ilmoitus_model.Person()
        employee_one.class_name = "employee"
        employee_one.first_name = "Piet"
        employee_one.last_name = "Hein"
        employee_one.email = "developers.42IN11EWa@gmail.com"
        employee_one.password = ilmoitus_auth.hash_secret("123456")
        employee_one.employee_number = 2
        employee_one.department = department_it.key
        employee_one.supervisor = supervisor_two.key
        employee_one.put()

        employee_two = ilmoitus_model.Person()
        employee_two.class_name = "employee"
        employee_two.first_name = "Axel"
        employee_two.last_name = "Klein"
        employee_two.email = "axel_klein@gmail.com"
        employee_two.password = ilmoitus_auth.hash_secret("123456")
        employee_two.employee_number = 3
        employee_two.department = department_it.key
        employee_two.supervisor = supervisor_one.key
        employee_two.put()

        employee_three = ilmoitus_model.Person()
        employee_three.class_name = "employee"
        employee_three.first_name = "Rik"
        employee_three.last_name = "van de Griendt"
        employee_three.email = "rikvdgriendt@gmail.com"
        employee_three.password = ilmoitus_auth.hash_secret("123456")
        employee_three.employee_number = 5
        employee_three.department = department_it.key
        employee_three.supervisor = supervisor_two.key
        employee_three.put()

        #HR
        employee_five = ilmoitus_model.Person()
        employee_five.class_name = "human_resources"
        employee_five.first_name = "Laura"
        employee_five.last_name = "Vermeulen"
        employee_five.email = "laura_vermeulen@gmail.com"
        employee_five.password = ilmoitus_auth.hash_secret("123456")
        employee_five.employee_number = 9
        employee_five.department = department_human_resources.key
        employee_five.supervisor = supervisor_three.key
        employee_five.put()

        employee_six = ilmoitus_model.Person()
        employee_six.class_name = "human_resources"
        employee_six.first_name = "Arjen"
        employee_six.last_name = "Drugov"
        employee_six.email = "a.drugovicj_drugov@gmail.com"
        employee_six.password = ilmoitus_auth.hash_secret("123456")
        employee_six.employee_number = 9
        employee_six.department = department_human_resources.key
        employee_six.supervisor = supervisor_three.key
        employee_six.put()

        #DECLARATION TYPES & SUBTYPES
        subtype_one = ilmoitus_model.DeclarationSubType(name="Zakelijke lunch/Diner met relaties")
        subtype_one.put()

        subtype_two = ilmoitus_model.DeclarationSubType(name="Logies/Verblijfskosten (eventueel incl. maaltijd)")
        subtype_two.put()

        subtype_three = ilmoitus_model.DeclarationSubType(name="Logies/Verblijfs-/Lunch-/Dinerkosten i.v.m. studie")
        subtype_three.put()

        subtype_four = ilmoitus_model.DeclarationSubType(name="Logies/Verblijfskosten buitenland")
        subtype_four.put()

        subtype_five = ilmoitus_model.DeclarationSubType(name="Lunch onderweg/i.v.m. meerwerk (max 15,- p.d.)")
        subtype_five.put()

        subtype_six = ilmoitus_model.DeclarationSubType(name="Diner onderweg/i.v.m. meerwerk (max 15,- p.d.)")
        subtype_six.put()

        type_one = ilmoitus_model.DeclarationType()
        type_one.name = "Maaltijd/Consumpties/Verblijf"
        type_one.sub_types = [subtype_one.key, subtype_two.key, subtype_three.key, subtype_four.key, subtype_five.key,
                              subtype_six.key]
        type_one.put()

        #DECLARATIONS
        #for employee one
        declaration_one = ilmoitus_model.Declaration()
        declaration_one.class_name = "open_declaration"
        declaration_one.created_by = employee_one.key
        declaration_one.created_at = datetime.datetime.now()
        declaration_one.assigned_to.append(employee_one.supervisor)
        declaration_one.comment = "Etentjes op zakenreis"
        declaration_one.items_count = 4
        declaration_one.items_total_price = 926
        declaration_one.put()

        #Declaration lines for declaration one
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_one.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 28
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_one.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 14
        line_two.declaration_sub_type = subtype_one.key
        line_two.put()

        line_three = ilmoitus_model.DeclarationLine()
        line_three.declaration = declaration_one.key
        line_three.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_three.cost = 8
        line_three.declaration_sub_type = subtype_six.key
        line_three.put()

        line_four = ilmoitus_model.DeclarationLine()
        line_four.declaration = declaration_one.key
        line_four.receipt_date = datetime.datetime.now() - datetime.timedelta(days=2)
        line_four.cost = 876
        line_four.declaration_sub_type = subtype_four.key
        line_four.put()

        declaration_two = ilmoitus_model.Declaration()
        declaration_two.class_name = "open_declaration"
        declaration_two.created_by = employee_one.key
        declaration_two.created_at = datetime.datetime.now()
        declaration_two.assigned_to.append(employee_one.supervisor)
        declaration_two.comment = "Tanken op zakenreis"
        declaration_two.items_count = 2
        declaration_two.items_total_price = 55
        declaration_two.put()

        #Declaration lines for declaration two
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_two.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 25
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_two.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 30
        line_two.declaration_sub_type = subtype_six.key
        line_two.put()

        declaration_three = ilmoitus_model.Declaration()
        declaration_three.class_name = "locked_declaration"
        declaration_three.created_by = employee_one.key
        declaration_three.created_at = datetime.datetime.now() - datetime.timedelta(days=3)
        declaration_three.assigned_to.append(employee_one.supervisor)
        declaration_three.comment = "Parkeren voor de vergadering met de rabobank"
        declaration_three.locked_at = datetime.datetime.now()
        declaration_three.supervisor_comment = "Deze moet pas de volgende maand betaald worden!"
        declaration_three.items_count = 3
        declaration_three.items_total_price = 60
        declaration_three.put()

        #Declaration lines for declaration three
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_three.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 30
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_three.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 10
        line_two.declaration_sub_type = subtype_six.key
        line_two.put()

        line_three = ilmoitus_model.DeclarationLine()
        line_three.declaration = declaration_three.key
        line_three.receipt_date = datetime.datetime.now() - datetime.timedelta(days=2)
        line_three.cost = 20
        line_three.declaration_sub_type = subtype_four.key
        line_three.put()

        declaration_six = ilmoitus_model.Declaration()
        declaration_six.class_name = "locked_declaration"
        declaration_six.created_by = employee_one.key
        declaration_six.created_at = datetime.datetime.now() - datetime.timedelta(days=3)
        declaration_six.assigned_to.append(employee_one.supervisor)
        declaration_six.comment = "Licenties voor Python development."
        declaration_six.locked_at = datetime.datetime.now()
        declaration_six.supervisor_comment = "Noteer deze ook even in de administratie voor de licenties"
        declaration_six.items_count = 1
        declaration_six.items_total_price = 89
        declaration_six.put()

        #Declaration lines for declaration six
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_six.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 89
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        declaration_seven = ilmoitus_model.Declaration()
        declaration_seven.class_name = "supervisor_approved_declaration"
        declaration_seven.created_by = employee_one.key
        declaration_seven.created_at = datetime.datetime.now() - datetime.timedelta(days=3)
        declaration_seven.assigned_to.append(employee_one.supervisor)
        declaration_seven.assigned_to.append(supervisor_two.supervisor)
        declaration_seven.comment = "Belkosten klanten voor project INTEGRITY."
        declaration_seven.locked_at = datetime.datetime.now() - datetime.timedelta(days=2)
        declaration_seven.submitted_to_human_resources_by = supervisor_two.supervisor  # employee one's supervisor's supervisor
        declaration_seven.supervisor_approved_at = datetime.datetime.now()
        declaration_seven.sent_to_human_resources_at = datetime.datetime.now()
        declaration_seven.supervisor_approved_by = supervisor_two.supervisor  # employee one's supervisor's supervisor
        declaration_seven.supervisor_comment = "Prioriteit & classificatie: ALPHA."
        declaration_seven.items_count = 2
        declaration_seven.items_total_price = 85
        declaration_seven.put()

        #Declaration lines for declaration seven
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_seven.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 35
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_seven.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 50
        line_two.declaration_sub_type = subtype_six.key
        line_two.put()

        declaration_eight = ilmoitus_model.Declaration()
        declaration_eight.class_name = "supervisor_approved_declaration"
        declaration_eight.created_by = employee_one.key
        declaration_eight.created_at = datetime.datetime.now() - datetime.timedelta(days=3)
        declaration_eight.assigned_to.append(employee_one.supervisor)
        declaration_eight.assigned_to.append(supervisor_two.supervisor)
        declaration_eight.comment = "Vliegkosten voor project INTEGRITY."
        declaration_eight.locked_at = datetime.datetime.now() - datetime.timedelta(days=2)
        declaration_eight.submitted_to_human_resources_by = supervisor_two.supervisor  # employee one's supervisor's supervisor
        declaration_eight.supervisor_approved_at = datetime.datetime.now()
        declaration_eight.sent_to_human_resources_at = datetime.datetime.now()
        declaration_eight.supervisor_approved_by = supervisor_two.supervisor  # employee one's supervisor's supervisor
        declaration_eight.supervisor_comment = "Prioriteit & classificatie: ALPHA."
        declaration_eight.items_count = 2
        declaration_eight.items_total_price = 20
        declaration_eight.put()

        #Declaration lines for declaration eight
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_eight.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 15
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_eight.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 5
        line_two.declaration_sub_type = subtype_six.key
        line_two.put()

        declaration_nine = ilmoitus_model.Declaration()
        declaration_nine.class_name = "human_resources_approved_declaration"
        declaration_nine.created_by = employee_one.key
        declaration_nine.created_at = datetime.datetime.now() - datetime.timedelta(days=31)
        declaration_nine.assigned_to.append(employee_one.supervisor)
        declaration_nine.comment = "Belkosten Janurai."
        declaration_nine.locked_at = datetime.datetime.now() - datetime.timedelta(days=27)
        declaration_nine.submitted_to_human_resources_by = employee_one.supervisor
        declaration_nine.supervisor_approved_at = datetime.datetime.now() - datetime.timedelta(days=27)
        declaration_nine.supervisor_approved_by = employee_one.supervisor
        declaration_nine.sent_to_human_resources_at = datetime.datetime.now() - datetime.timedelta(days=25)
        declaration_nine.will_be_payed_out_on = datetime.datetime.now() - datetime.timedelta(days=14)
        declaration_nine.human_resources_approved_by = employee_six.key
        declaration_nine.human_resources_approved_at = datetime.datetime.now() - datetime.timedelta(days=20)
        declaration_nine.items_count = 1
        declaration_nine.items_total_price = 87
        declaration_nine.put()

        #Declaration lines for declaration nine
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_nine.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 87
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        declaration_ten = ilmoitus_model.Declaration()
        declaration_ten.class_name = "human_resources_approved_declaration"
        declaration_ten.created_by = employee_one.key
        declaration_ten.created_at = datetime.datetime.now() - datetime.timedelta(days=31)
        declaration_ten.assigned_to.append(employee_one.supervisor)
        declaration_ten.comment = "Verblijfskosten Januari."
        declaration_ten.locked_at = datetime.datetime.now() - datetime.timedelta(days=27)
        declaration_ten.submitted_to_human_resources_by = employee_one.supervisor
        declaration_ten.supervisor_approved_at = datetime.datetime.now() - datetime.timedelta(days=26)
        declaration_ten.supervisor_approved_by = employee_one.supervisor
        declaration_ten.sent_to_human_resources_at = datetime.datetime.now() - datetime.timedelta(days=26)
        declaration_ten.will_be_payed_out_on = datetime.datetime.now() - datetime.timedelta(days=14)
        declaration_ten.human_resources_approved_by = employee_six.key
        declaration_ten.human_resources_approved_at = datetime.datetime.now() - datetime.timedelta(days=18)
        declaration_ten.items_count = 2
        declaration_ten.items_total_price = 140
        declaration_ten.put()

        #Declaration lines for declaration ten
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_ten.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 55
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_ten.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 85
        line_two.declaration_sub_type = subtype_six.key
        line_two.put()

        declaration_eleven = ilmoitus_model.Declaration()
        declaration_eleven.class_name = "human_resources_declined_declaration"
        declaration_eleven.created_by = employee_one.key
        declaration_eleven.created_at = datetime.datetime.now() - datetime.timedelta(days=31)
        declaration_eleven.assigned_to.append(employee_one.supervisor)
        declaration_eleven.comment = "Verblijfskosten Januari."  # the same on purpose!
        declaration_eleven.locked_at = datetime.datetime.now() - datetime.timedelta(days=27)
        declaration_eleven.submitted_to_human_resources_by = employee_one.supervisor
        declaration_eleven.supervisor_approved_at = datetime.datetime.now() - datetime.timedelta(days=26)
        declaration_eleven.supervisor_approved_by = employee_one.supervisor
        declaration_eleven.sent_to_human_resources_at = datetime.datetime.now() - datetime.timedelta(days=26)
        declaration_eleven.declined_by = employee_six.key
        declaration_eleven.human_resources_comment = \
            "Muhammed heeft er een dubbel doorgestuurd; deze wordt niet uitbetaald."
        declaration_eleven.human_resources_declined_at = datetime.datetime.now() - datetime.timedelta(days=18)
        declaration_eleven.items_count = 2
        declaration_eleven.items_total_price = 140
        declaration_eleven.put()

        #Declaration lines for declaration eleven
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_eleven.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 55
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_eleven.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 85
        line_two.declaration_sub_type = subtype_six.key
        line_two.put()

        declaration_twelve = ilmoitus_model.Declaration()
        declaration_twelve.class_name = "supervisor_declined_declaration"
        declaration_twelve.created_by = employee_one.key
        declaration_twelve.created_at = datetime.datetime.now() - datetime.timedelta(days=12)
        declaration_twelve.assigned_to.append(employee_one.supervisor)
        declaration_twelve.comment = "Zakenlunches voor Februari."
        declaration_twelve.locked_at = datetime.datetime.now() - datetime.timedelta(days=9)
        declaration_twelve.declined_by = employee_one.supervisor
        declaration_twelve.supervisor_declined_at = datetime.datetime.now() - datetime.timedelta(days=4)
        declaration_twelve.supervisor_comment = "Deze worden niet vergoed aangezien ze niet vooraf zijn besproken."
        declaration_twelve.items_count = 2
        declaration_twelve.items_total_price = 47
        declaration_twelve.put()

        #Declaration lines for declaration twelve
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_twelve.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 27
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_twelve.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 20
        line_two.declaration_sub_type = subtype_six.key
        line_two.put()

        declaration_thirteen = ilmoitus_model.Declaration()
        declaration_thirteen.class_name = "human_resources_approved_declaration"
        declaration_thirteen.created_by = employee_one.key
        declaration_thirteen.created_at = datetime.datetime.now() - datetime.timedelta(days=31)
        declaration_thirteen.assigned_to.append(employee_one.supervisor)
        declaration_thirteen.comment = "Reiskosten Janurai."
        declaration_thirteen.locked_at = datetime.datetime.now() - datetime.timedelta(days=27)
        declaration_thirteen.submitted_to_human_resources_by = employee_one.supervisor
        declaration_thirteen.supervisor_approved_at = datetime.datetime.now() - datetime.timedelta(days=27)
        declaration_thirteen.supervisor_approved_by = employee_one.supervisor
        declaration_thirteen.sent_to_human_resources_at = datetime.datetime.now() - datetime.timedelta(days=25)
        declaration_thirteen.will_be_payed_out_on = datetime.datetime.now() - datetime.timedelta(days=14)
        declaration_thirteen.human_resources_approved_by = employee_six.key
        declaration_thirteen.human_resources_approved_at = datetime.datetime.now() - datetime.timedelta(days=20)
        declaration_thirteen.items_count = 1
        declaration_thirteen.items_total_price = 45
        declaration_thirteen.put()

        #Declaration lines for declaration thirteen
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_thirteen.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 45
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        #for employee two
        declaration_four = ilmoitus_model.Declaration()
        declaration_four.class_name = "open_declaration"
        declaration_four.created_by = employee_two.key
        declaration_four.assigned_to.append(employee_two.supervisor)
        declaration_four.comment = "Vlucht kosten zakenreis naar engeland"
        declaration_four.items_count = 2
        declaration_four.items_total_price = 155
        declaration_four.put()

        #Declaration lines for declaration four
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_four.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 110
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()

        line_two = ilmoitus_model.DeclarationLine()
        line_two.declaration = declaration_four.key
        line_two.receipt_date = datetime.datetime.now() - datetime.timedelta(days=6)
        line_two.cost = 45
        line_two.declaration_sub_type = subtype_six.key
        line_two.put()

        #for employee three
        declaration_five = ilmoitus_model.Declaration()
        declaration_five.class_name = "supervisor_declined_declaration"
        declaration_five.created_by = employee_two.key
        declaration_five.assigned_to.append(employee_two.supervisor)
        declaration_five.comment = "Bedrijfsuitje"
        declaration_five.declined_by = employee_two.supervisor
        declaration_five.submitted_to_human_resources_by = employee_two.supervisor
        declaration_five.items_count = 1
        declaration_five.items_total_price = 25
        declaration_five.put()

        #Declaration lines for declaration five
        line_one = ilmoitus_model.DeclarationLine()
        line_one.declaration = declaration_five.key
        line_one.receipt_date = datetime.datetime.now() - datetime.timedelta(days=7)
        line_one.cost = 25
        line_one.declaration_sub_type = subtype_one.key
        line_one.put()


class ClearHandler(webapp2.RequestHandler):
    @staticmethod
    def clear_data():
        for department in ilmoitus_model.Department.query():
            department.key.delete()
        for person in ilmoitus_model.Person.query():
            person.key.delete()
        for declaration in ilmoitus_model.Declaration.query():
            declaration.key.delete()
        for sub_type in ilmoitus_model.DeclarationSubType.query():
            sub_type.key.delete()
        for declaration_type in ilmoitus_model.DeclarationType.query():
            declaration_type.key.delete()
        for declaration_line in ilmoitus_model.DeclarationLine.query():
            declaration_line.key.delete()
        for attachment in ilmoitus_model.Attachment.query():
            attachment.key.delete()

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
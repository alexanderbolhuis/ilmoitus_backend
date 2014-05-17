__author__ = 'Sjors van Lemmen'

from handlers.declaration_list import *
from handlers.declaration_handler import *
from handlers.currentuser_handler import *
from ilmoitus_auth import *
from response_module import *
import json
import data_bootstrapper
from error_response_module import give_error_response

import ilmoitus_auth
import base64


class DefaultHandler(BaseRequestHandler):
    def get(self):
        html_data = """
            <html>
             <head>
              <title>Default Home Page</title>
             </head>
             <body>
              <h1>Default Home Page</h1>
                <p>This is the default home page, meaning that the requested url:<br />
                   <a href=\"""" + str(self.request.url) + """\">""" + str(self.request.uri) + """</a><br />
                   did NOT match on any known urls. Check for typo's and try again.
                </p>
             </body>
            </html>"""
        response_module.give_hard_response(self, html_data)


class AllEmployeesHandler(BaseRequestHandler):
    def get(self):
        if self.is_logged_in():
            respond_with_object_collection_by_class(self,
                                                    Person,
                                                    self.get_header_limit(),
                                                    self.get_header_offset())


class SpecificEmployeeDetailsHandler(BaseRequestHandler):
    def get(self, employee_id):
        if self.is_logged_in():
            #TODO check if user is allowed to see this data (discussion needed)
            response_module.respond_with_object_details_by_id(self, Person, employee_id)


class AllDeclarationTypesHandler(BaseRequestHandler):
    def get(self):
        query = ilmoitus_model.DeclarationType.query()
        query_result = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

        if len(query_result) != 0:
            response_module.give_response(self, json.dumps(
                map(lambda declaration_type: declaration_type.get_object_as_data_dict(), query_result)))
        else:
            give_error_response(self, 404, "There are no DeclarationTypes",
                                "Add some DeclarationTypes to the data store")


class AllDeclarationTypeSubTypeHandler(BaseRequestHandler):
    def get(self, declaration_type_id):
        safe_id = 0
        try:
            safe_id = long(declaration_type_id)
        except ValueError:
            give_error_response(self, 500, "the given id isn't an int (" + str(declaration_type_id) + ")")

        item = ilmoitus_model.DeclarationType.get_by_id(safe_id)

        if item is None:
            give_error_response(self, 404, "there is no declarationType with that id")

        if len(item.sub_types) is 0:
            give_error_response(self, 404, "there are no DeclarationSubTypes associated to this DeclarationType")

        query = ilmoitus_model.DeclarationSubType.query(ilmoitus_model.DeclarationSubType.key.IN(item.sub_types))
        sub_types = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())
            #[res for res in query.fetch() if res.key in item.sub_types]

        if len(sub_types) is 0:
            give_error_response(self, 404, "there are no DeclarationSubTypes associated to this DeclarationType")

        response_module.give_response(self, json.dumps(map(lambda sub_type: sub_type.get_object_as_data_dict(),
                                                           sub_types)))


class AllDeclarationSubTypesHandler(BaseRequestHandler):
    def get(self):
        query = ilmoitus_model.DeclarationSubType.query()

        query_result = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

        if query_result is None:
            give_error_response(self, 404, "there are no DeclarationSubTypes",
                                "insert some DeclarationSubTypes in the datastore")
        else:
            response_module.respond_with_existing_model_object_collection(self, query_result)


#Don't use this handler when retrieving all declaration info. Use getSpecificDeclaration instead!
class SpecificDeclarationLinesHandler(BaseRequestHandler):
    def get(self, declaration_id):
        person_data = ilmoitus_auth.get_current_person(self)
        current_user = person_data["person_value"]

        if current_user is None:
            give_error_response(self, 401, "De declaratie regels kunnen niet worden opgehaald omdat u niet "
                                           "de juiste permissies heeft.",
                                "current_user is None")

        if str.isdigit(declaration_id):
            # Does declaration exist
            declaration = ilmoitus_model.Declaration.get_by_id(long(declaration_id))
            if declaration is None:
                give_error_response(self, 404, "Kan geen declaratie regels ophalen. De opgegeven declaratie bestaat niet",
                                    "declaration_id not found")

            if len(declaration.lines) != 0:
                declarationline_query = ilmoitus_model.DeclarationLine.query(ilmoitus_model.DeclarationLine.key.IN(declaration.lines))
                query_result = declarationline_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

                if query_result is None:
                    give_error_response(self, 404, "De declaratie heeft geen regels.",
                                        "No DeclarationLines found with the keys in declaration.lines")
            else:
                give_error_response(self, 404, "De declaratie heeft geen regels.",
                                    "declaration.lines array has no elements")

        else:
            give_error_response(self, 400, "Kan geen declaratie regels ophalen.",
                                "declaration id can only be of the type integer.")

        response_module.respond_with_existing_model_object_collection(self, query_result)


#Don't use this handler when retrieving all declaration info. Use getSpecificDeclaration instead!
class SpecificDeclarationAttachmentsHandler(BaseRequestHandler):
    def get(self, declaration_id):
        person_data = ilmoitus_auth.get_current_person(self)
        current_user = person_data["person_value"]

        if current_user is None:
            give_error_response(self, 401, "De bijlagen kunnen niet worden opgehaald omdat u niet "
                                           "de juiste permissies heeft.",
                                "current_user is None")

        if str.isdigit(declaration_id):
            # Does declaration exist
            declaration = ilmoitus_model.Declaration.get_by_id(long(declaration_id))
            if declaration is None:
                give_error_response(self, 404, "Kan geen bijlagen ophalen. De opgegeven declaratie bestaat niet",
                                    "declaration_id not found")

            if len(declaration.attachments) != 0:
                query = ilmoitus_model.Attachment.query(ilmoitus_model.Attachment.key.IN(declaration.attachments))
                attachments = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

                if attachments is None:
                    give_error_response(self, 404, "De declaratie heeft geen bijlagen.",
                                        "No attachments found with the keys in declaration.attachments")
            else:
                give_error_response(self, 404, "De declaratie heeft geen bijlagen.",
                                    "Declaration.attachments array has no elements")

        else:
            give_error_response(self, 400, "Kan geen bijlagen ophalen.",
                                "declaration id can only be of the type integer.")

        post_data = []
        for attachment in attachments:
            item = {"id": attachment.key.integer_id(), "name": attachment.name}
            post_data.append(item)

        response_module.give_response(self, json.dumps(post_data))


class SpecificAttachmentHandler(BaseRequestHandler):
    def get(self, attachment_id):
        person_data = ilmoitus_auth.get_current_person(self)
        current_user = person_data["person_value"]

        if current_user is None:
            give_error_response(self, 401, "De bijlage kan niet worden opgehaald omdat u niet "
                                           "de juiste permissies heeft.",
                                "current_user is None")

        if str.isdigit(attachment_id):
            attachment = ilmoitus_model.Attachment.get_by_id(long(attachment_id))
            if attachment is None:
                    give_error_response(self, 404, "Kan de opgevraagde bijlage niet vinden.",
                                        "attachment id does not exist in the database.")
        else:
            give_error_response(self, 400, "Kan de opgevraagde bijlage niet vinden.",
                                "attachment id can only be of the type integer.")

        base64_string = attachment.file.split(",")[1]
        mime = attachment.file.split(":")[1].split(";")[0]
        self.response.headers['Content-Type'] = mime
        self.response.write(base64.b64decode(base64_string))


class SpecificEmployeeTotalDeclarationsHandler(BaseRequestHandler):
    def get(self, employee_id):
        # Only supervisors can perform the actions in this handler: check for that first
        current_person_data = ilmoitus_auth.get_current_person(self)
        if "user_is_logged_in" not in current_person_data.keys() or \
                not current_person_data["user_is_logged_in"]:  # if logged in is false
            give_error_response(self, 401,
                                "Er is niemand ingelogd.",
                                "get_current_person returned a False value for user_is_logged_in")

        current_person_object = current_person_data["person_value"]
        if current_person_object is None:
            give_error_response(self, 401, "De ingelogd persoon in onbekend binnen de applicatie"
                                           " of de ingelogde persoon heeft niet de rechten van een"
                                           " leidinggevende binnen de applicatie.",
                                "person_value key in get_current_person was None")

        # Does employee exist
        employee = ilmoitus_model.Person.get_by_id(int(employee_id))
        if employee is None:
            give_error_response(self, 404, "Werknemer bestaat niet",
                                        "Employee not found")

        # Find declarations for employee
        accepted_declarations = ilmoitus_model.Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="human_resources_approved_declaration").fetch()
        accepted = len(accepted_declarations)

        open_declarations = ilmoitus_model.Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="open_declaration").fetch()
        open = len(open_declarations)

        sv_denied_declarations = ilmoitus_model.Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="supervisor_declined_declaration").fetch()
        sv_denied = len(sv_denied_declarations)

        hr_denied_declarations = ilmoitus_model.Declaration.gql("WHERE created_by = :cb AND class_name = :cn", cb=employee.key, cn="human_resources_declined_declaration").fetch()
        hr_denied = len(hr_denied_declarations)

        total_cost = 0

        for declaration in accepted_declarations:
            total_cost = total_cost + declaration.items_total_price

        response_dict = {"id": employee_id, "open_declarations": open, "accepted_declarations": accepted, "denied_declarations": (hr_denied + sv_denied), "total_declarated_price": total_cost}
        response_module.give_response(self, json.dumps(response_dict))


application = webapp.WSGIApplication(
    [
        #Current user handlers
        ('/current_user/details', CurrentUserDetailsHandler),
        ('/current_user/settings', CurrentUserSettingsHandler),
        ('/current_user/associated_declarations', CurrentUserAssociatedDeclarationsHandler),
        ('/current_user/supervisors', CurrentUserSupervisorsHandler),

        #Employee handlers
        ('/employees', AllEmployeesHandler),
        ('/employee/(.*)/total_declarations', SpecificEmployeeTotalDeclarationsHandler),
        ('/employee/(.*)', SpecificEmployeeDetailsHandler),

        #Declaration list
        ('/declarations/employee', AllDeclarationsForEmployeeHandler),
        ('/declarations/supervisor', AllDeclarationsForSupervisorHandler),
        ('/declarations/hr', AllDeclarationsForHumanResourcesHandler),

        #Declaration type list
        ('/declarationtypes', AllDeclarationTypesHandler),
        ('/declarationtype/(.*)', AllDeclarationTypeSubTypeHandler),
        ('/declarationsubtypes', AllDeclarationSubTypesHandler),

        #Declaration handlers
        ('/declaration/(.*)/lock', OpenToLockedDeclarationResourcesHandler),
        ('/declaration/(.*)/forward_to_supervisor/(.*)', ForwardDeclarationHandler),
        ('/declaration/(.*)/decline_by_supervisor', DeclineBySupervisorHandler),
        ('/declaration/(.*)/approve_by_supervisor', ApproveBySupervisorHandler),
        ('/declaration/(.*)/decline_by_hr', DeclineByHumanResourcesHandler),
        ('/declaration/(.*)/approve_by_hr', ApproveByHumanResourcesHandler),
        ('/declaration/(.*)', SpecificDeclarationHandler),
        ("/declaration", NewDeclarationHandler),

        #Attchment handlers
        ('/attachment/(.*)', SpecificAttachmentHandler),

        #Authencation
        ('/auth/login', LoginHandler),
        ('/auth/logout', LogoutHandler),
        ('/auth', AuthorizationStatusHandler),

        #Etc
        ('/clear', data_bootstrapper.ClearHandler),
        ('/fill', data_bootstrapper.FillHandler),
        ('/create', data_bootstrapper.CreateDataHandler),
        ('.*', DefaultHandler)
    ],
    debug=True)  # if debug is set to false,
# any uncaught exceptions will only trigger a server error without any details
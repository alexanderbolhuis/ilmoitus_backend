from unicodedata import decimal

__author__ = 'Sjors van Lemmen'
import webapp2 as webapp
import response_module
import ilmoitus_model
import json
import datetime
import logging
import data_bootstrapper
from google.appengine.api import users
from google.appengine.ext import ndb
from error_response_module import give_error_response


def get_current_person(class_name=None):
    """
     Global function that will retrieve the user that is currently logged in (through Google's users API)
     and fetch the person model object of this application that belongs to it through the email field.

     :param class_name: (Optional) A reference to a person model class that should be used to find
     the model class object that belongs to the logged in user. If not provided, model.Person will be used.

     :returns: A dictionary containing two key-value pairs:

         -"user_is_logged_in": Boolean that indicates whether a user is logged into the users API of Google.

         -"person_value": Model object of the Person type (or any subclass, indicated by the person_class_reference
        parameter). If there is either no user logged into Google's users API _OR_ the logged in user isn't found
        in the model class, this will be None
    """
    current_logged_in_user = users.get_current_user()
    return_data = {"user_is_logged_in": False, "person_value": None}
    if current_logged_in_user is not None:
        return_data["user_is_logged_in"] = True
        if class_name is None:
            person_query = ilmoitus_model.Person.query(ilmoitus_model.Person.email == current_logged_in_user.email())
        else:
            person_query = ilmoitus_model.Person.query(ilmoitus_model.Person.email == current_logged_in_user.email(),
                                                       ilmoitus_model.Person.class_name == class_name)
        query_result = person_query.get()
        if query_result is not None:
            return_data["person_value"] = query_result
    return return_data


class BaseRequestHandler(webapp.RequestHandler):
    """
    Wrapper class that will allow all other handler classes to make easily read what the
    limit and/or offset is for a request
    """

    def get_header_limit(self):
        limit = self.request.get("limit", default_value=20)
        return limit

    def get_header_offset(self):
        offset = self.request.get("offset", default_value=0)
        return offset

    def handle_exception(self, exception, debug):
        """
        Overrides function in webapp.RequestHandler.

        This function will catch any HTTP exceptions that can be raised by a .abort() function call within
        a handler that inherits from the BaseRequestHandler class. When this happens, this function will
        log the request and if the application is in debug mode, also the exception (basically the complete
        stack trace).

        Lastly, this function will write the full body of the request and set the status of the response
        to the code of the exception. It's important to note that the body of the request is used as a
        response, since it's through this property that any data will be sent back to the user (such as
        a message indicating what went wrong, status and error codes, etc.). This is also the only real
        custom functionality that this function provides (the rest is default, but a call to the base method
        could cause problems in some cases).

        :param exception: The exception that was raised by this handler or any handler that inherits from this handler.

        :param debug: Boolean indicating whether the application is in debug mode or not. Will be automatically
            detected.
        """
        logging.debug(self.request)
        if debug:
            logging.exception(exception)

        self.response.write(self.request.body)
        try:
            self.response.set_status(exception.code)
        except AttributeError:
            #The caught exception was not a HTTPException; we don't know how to handle this so just raise it again
            raise exception


class DefaultHandler(BaseRequestHandler):
    def get(self):
        html_data = """
<html>
 <head>
  <title>Default Home Page</title>
 </head>
 <body>
  <h1>Default Home Page</h1>
    <p>This is the default home page, meaning that the requested url:<br /><a href=\"""" + str(self.request.url) \
                    + """\">""" + str(self.request.uri) + """</a><br />did NOT
    match on any known urls. Check for typo's and try again.</p>
 </body>
</html>"""
        response_module.give_hard_response(self, html_data)


class AllPersonsHandler(BaseRequestHandler):
    def get(self):
        response_module.respond_with_object_collection_by_class(self,
                                                                ilmoitus_model.Person,
                                                                self.get_header_limit(),
                                                                self.get_header_offset())


class SpecificPersonHandler(BaseRequestHandler):
    def get(self, person_id):
        response_module.respond_with_object_details_by_id(self,
                                                          ilmoitus_model.Person,
                                                          person_id)  # Since NDB, keynames are also valid ID's!


class AllEmployeesHandler(BaseRequestHandler):
    def get(self):
        response_module.respond_with_object_collection_by_class(self,
                                                                ilmoitus_model.Person,
                                                                self.get_header_limit(),
                                                                self.get_header_offset(),
                                                                "employee")


class SpecificEmployeeHandler(BaseRequestHandler):
    def get(self, employee_id):
        response_module.respond_with_object_details_by_id(self,
                                                          ilmoitus_model.Person,
                                                          employee_id)


class AuthorizationStatusHandler(BaseRequestHandler):
    def get(self):
        """
         Note on this function: we don't need to check if the user is logged in. If he is not logged in _OR_
         he doesn't exist in the model, we return the same dictionary. This means that if we were to check on login
         is True, we still have to check if person value is not None. by directly checking person is not None, we
         get the same result with less code.
        """
        person_data = get_current_person()
        person = person_data["person_value"]
        if person is not None:
            #Create a default data dictionary to limit code duplication
            response_data = {"person_id": person.key.integer_id(), "is_logged_in": True,
                             "is_application_admin": users.is_current_user_admin()}
            response_module.give_response(self, json.dumps(response_data))
        else:
            #Person is not known in the application's model
            response_module.give_response(self, json.dumps({"is_logged_in": False}))


class LoginHandler(BaseRequestHandler):
    def get(self):
        person_data = get_current_person()
        person = person_data["person_value"]
        if person is None:
            self.redirect(users.create_login_url('/auth/login'))
            # We will return to the same url after logging in since this handler will than check if the login
            # was really successful, and automatically redirect to the main page if so.
        else:
            #TODO: redirect here to the actual "main" page
            #TODO: research/discuss how to make this work cross platform (how will iOS & Android handle redirects?)
            self.redirect("/main_page")


class LogoutHandler(BaseRequestHandler):
    def get(self):
        person_data = get_current_person()
        person = person_data["person_value"]
        if person is not None:
            self.redirect(users.create_logout_url('/auth/logout/'))
            # We will return to the same url after logging out since this handler will than check if the login
            # was really successful, and automatically redirect to the login page if so.
        else:
            #TODO: redirect here to the actual login page
            #TODO: research/discuss how to make this work cross platform (how will iOS & Android handle redirects?)
            self.redirect("/login_page")


class AllDeclarationsForEmployeeHandler(BaseRequestHandler):
    def get(self):
        #model.Employee as param since this handler handles calls from their POV.
        person_data = get_current_person("employee")
        person = person_data["person_value"]

        if person is not None:
            declaration_query = ilmoitus_model.Declaration.query(ilmoitus_model.Declaration.created_by == person.key)

            query_result = declaration_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            response_module.respond_with_existing_model_object_collection(self, query_result)
        else:
            #TODO: error messages:
            #User is not logged in/registered; he/she needs to login first
            self.abort(401)


class SpecificEmployeeDetailsHandler(BaseRequestHandler):
    def get(self, employee_id):
        response_module.respond_with_object_details_by_id(self,
                                                          ilmoitus_model.Person,
                                                          employee_id)


class AllDeclarationsForSupervisor(BaseRequestHandler):
    def get(self):
        person_data = get_current_person("supervisor")
        person = person_data["person_value"]

        if person is not None and person.class_name == 'supervisor':

            declaration_query = ilmoitus_model.Declaration.query(
                ilmoitus_model.Declaration.class_name == 'open_declaration',
                ilmoitus_model.Declaration.assigned_to == person.key)
            query_result = declaration_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            response_module.respond_with_existing_model_object_collection(self, query_result)
        else:
            #user does not have the appropriate permissions or isn't logged in at all.
            self.abort(401)


class CurrentUserDetailsHandler(BaseRequestHandler):
    def get(self):
        current_user_data = get_current_person()
        user_is_logged_in = current_user_data["user_is_logged_in"]
        if user_is_logged_in is True:
            current_user = current_user_data["person_value"]
            if current_user is not None:
                response_module.give_response(self, current_user.get_object_json_data())
            else:
                print "Not Found"
                self.abort(404)
        else:
            print "Unauthorized"
            self.abort(401)


class UserSettingsHandler(BaseRequestHandler):
    def get(self):
        employee = get_current_person()
        if employee is not None:
            response_module.give_response(self, json.dumps(employee.details()))
            response_module.give_response(self, employee.get_object_json_data())
            #TODO what to do when employee is None?

    def put(self):
        employee = get_current_person()
        if employee is not None:
            employee.wants_email_notifications = bool(self.request.get("wants_email_notifications"))
            employee.wants_phone_notifications = bool(self.request.get("wants_phone_notifications"))
            #TODO what to do when employee is None?


class SetLockedToSupervisorApprovedDeclarationHandler(BaseRequestHandler):
    def put(self):
        #Only supervisors can perform the actions in this handler: check for that first
        current_person_data = get_current_person("Supervisor")
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
        declaration_data = None
        try:
            declaration_data = json.loads(self.request.body)
        except ValueError:
            if self.request.body is None or len(self.request.body) <= 0:
                give_error_response(self, 400, "Er is geen declratie opgegeven om aan te passen.",
                                    "Request body was None.")
        if declaration_data is None or not isinstance(declaration_data, dict):
            give_error_response(self, 400, "Er is geen declratie opgegeven om aan te passen.",
                                "Request.body did not contain valid json data")

        declaration_id = None
        try:
            declaration_id = long(declaration_data["id"])
        except KeyError:
            give_error_response(self, 400, "De opgegeven data bevat geen identificatie voor een declaratie.",
                                "The body doesn't contain an ID key.")
        except (TypeError, ValueError):
            give_error_response(self, 400,
                                "De opgegeven data bevat een ongeldige identificatie voor een declaratie.",
                                "Failed to parse the value of the ID key in the body to a long.")

        declaration_object = ilmoitus_model.Declaration.get_by_id(declaration_id)
        try:
            if current_person_object.key not in declaration_object.assigned_to:
                give_error_response(self, 401, "Deze declaratie is niet aan de leidinggevende toegewezen die op"
                                               " dit moment is ingelogd", "current_person_object's id was not in the"
                                                                          " declaration_object's asigned_to list.")
            if declaration_object.class_name != "locked_declaration":
                give_error_response(self, 422,
                                    "De opgegeven declaratie is niet gesloten en kan dus niet goedgekeurd worden.",
                                    "Class name of fetched object was not equal locked_declaration")

            declaration_object.class_name = "supervisor_approved_declaration"
            declaration_object.submitted_to_human_resources_by = current_person_object.key
            declaration_object.supervisor_approved_at = datetime.datetime.now()
            if "supervisor_comment" in declaration_data.keys():
                #No need to check if the string parsing could fail here; json will always have data that
                #can be parsed to a string
                declaration_object.supervisor_comment = str(declaration_data["supervisor_comment"])

        except AttributeError:
            give_error_response(self, 404,
                                "De opgegeven identificatie is onbekend en behoort tot geen enkele declaratie.",
                                "Query result from the value of the ID key of the body returned None.")
        declaration_object.put()
        response_module.give_response(self, json.dumps(declaration_object.get_object_as_data_dict()))


class CurrentUserSupervisors(BaseRequestHandler):
    def get(self):
        #TODO now this function gets all supervisors, we need to know if it only need supervisors of current person
        current_user_data = get_current_person()
        user_is_logged_in = current_user_data["user_is_logged_in"]
        if user_is_logged_in is True:
            supervisor_query = ilmoitus_model.Person.query(ilmoitus_model.Person.class_name == "supervisor")
            query_result = supervisor_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            response_module.respond_with_existing_model_object_collection(self, query_result)
        else:
            self.abort(401)


class AllDeclarationsForHumanResourcesHandler(BaseRequestHandler):
    def get(self):
        person_data = get_current_person("human_resources")
        person = person_data["person_value"]
        if person is not None:
            if person.class_name == "human_resources":  # person.key.class_name == "human_resources":
                declaration_query = ilmoitus_model.Declaration.query(
                    ilmoitus_model.Declaration.class_name == "supervisor_approved_declaration")

                query_result = declaration_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

                response_module.respond_with_existing_model_object_collection(self, query_result)
            else:
                #User is not authorised
                self.abort(401)
        else:
            #TODO: error messages:
            #User is not logged in/registered; he/she needs to login first
            self.abort(401)


class CurrentUserAssociatedDeclarations(BaseRequestHandler):
    def get(self):
        person_data = get_current_person()
        current_user = person_data["person_value"]

        key = current_user.key

        declaration = ilmoitus_model.Declaration
        query = ilmoitus_model.Declaration.query(ndb.OR(declaration.created_by == key,
                                                        declaration.assigned_to == key,  # TODO fix the list search
                                                        declaration.supervisor_approved_by == key,
                                                        declaration.submitted_to_human_resources_by == key,
                                                        declaration.human_resources_declined_by == key,
                                                        declaration.human_resources_approved_by == key,
                                                        declaration.declined_by == key))
        query_result = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())
        if len(query_result) != 0:
            response_module.give_response(self, json.dumps(
                map(lambda declaration_item: declaration_item.get_object_as_data_dict(), query_result)))
        else:
            self.abort(404)


class SpecificDeclarationHandler(BaseRequestHandler):
    def get(self, declaration_id):
        person_data = get_current_person()
        current_user = person_data["person_value"]

        employee_rights = current_user.class_name

        key = current_user.key
        result = ilmoitus_model.Declaration.get_by_id(long(declaration_id))

        flag_none_exists = True
        if result is not None:
            flag_none_exists = False
            declaration_data = result

            flag_auth = False

            if employee_rights == 'employee':
                if declaration_data.created_by == key:
                    flag_auth = True

            elif employee_rights == 'supervisor' and declaration_data.class_name == 'open_declaration':
                if declaration_data.assigned_to[0] == key:
                    flag_auth = True

            elif employee_rights == 'human_resources' and declaration_data.class_name == \
                                    'supervisor_approved_declaration':
                if declaration_data.submitted_to_human_resources_by is not None:
                    flag_auth = True
            else:
                flag_auth = False

        if flag_none_exists is False:
            if flag_auth is True:
                response_module.give_response(self, declaration_data.get_object_json_data())
            else:
                #TODO: error messages:
                self.abort(401)
        else:
            #TODO: error messages:
            self.abort(404)

application = webapp.WSGIApplication(
    [
        ('/persons', AllPersonsHandler),
        ('/persons/(.*)', SpecificPersonHandler),
        ('/user/settings/', UserSettingsHandler),
        ('/employees', AllEmployeesHandler),
        ('/employees/details/(.*)', SpecificEmployeeDetailsHandler),
        ('/employees/(.*)', SpecificEmployeeHandler),
        ('/declarations/hr', AllDeclarationsForHumanResourcesHandler),
        ('/supervisors/', CurrentUserSupervisors),
        ('/declarations/employee', AllDeclarationsForEmployeeHandler),
        ('/current_user/associated_declarations', CurrentUserAssociatedDeclarations),
        ('/current_user/details', CurrentUserDetailsHandler),
        ('/declarations/supervisor', AllDeclarationsForSupervisor),
        ('/declaration/(.*)', SpecificDeclarationHandler),
        ('/auth/login', LoginHandler),
        ('/auth/logout', LogoutHandler),
        ('/auth/(.*)', AuthorizationStatusHandler),  # needs to be bellow other auth handlers!
        ('/clear', data_bootstrapper.ClearHandler),
        ('/fill', data_bootstrapper.FillHandler),
        ('/create', data_bootstrapper.CreateDataHandler),
        ('.*', DefaultHandler)
    ],
    debug=True)  # if debug is set to false,
# any uncaught exceptions will only trigger a server error without any details
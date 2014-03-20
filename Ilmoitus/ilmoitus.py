__author__ = 'Sjors van Lemmen'
import webapp2 as webapp
import response_module
import model
import json
import data_bootstrapper
from google.appengine.api import users


def get_current_person(person_class_reference=model.User):
    """
     Global function that will retrieve the user that is currently logged in (through Google's users API)
     and fetch the person model object of this application that belongs to it through the email field.

     :param person_class_reference: (Optional) A reference to a person model class that should be used to find
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
        person_query = person_class_reference.query().filter(person_class_reference.email ==
                                                             current_logged_in_user.email())
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
        response_module.respond_with_object_collection_by_class(self,  # passing self is unusual, but needed to generate
                                                                model.User,  # an HTTP response
                                                                self.get_header_limit(),
                                                                self.get_header_offset())


class SpecificPersonHandler(BaseRequestHandler):
    def get(self, person_id):
        response_module.respond_with_object_details_by_id(self,
                                                          model.User,
                                                          person_id)  # Since NDB, keynames are also valid ID's!


class AllEmployeesHandler(BaseRequestHandler):
    def get(self):
        response_module.respond_with_object_collection_by_class(self,
                                                                model.User,  # Will only get Employees or subclasses
                                                                self.get_header_limit(),
                                                                self.get_header_offset())


class SpecificEmployeeHandler(BaseRequestHandler):
    def get(self, employee_id):
        response_module.respond_with_object_details_by_id(self,
                                                          model.User,
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



class AllOpenDeclarationsForEmployeeHandler(BaseRequestHandler):
    def get(self):
        #model.Employee as param since this handler handles calls from their POV.
        person_data = get_current_person(model.User)
        person = person_data["person_value"]
        if person is not False:
            declaration_query = model.Declaration.query(model.Declaration.created_by == person.key)
            query_result = declaration_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            response_module.respond_with_existing__model_object_collection(self, query_result)
        else:
            #TODO: error messages:
            #User is not logged in/registered; he/she needs to login first
            self.abort(401)


class SpecificEmployeeDetailsHandler(BaseRequestHandler):
    def get(self, employee_id):
        response_module.respond_with_object_details_by_id(self,
                                                          model.Employee,
                                                          employee_id)


class CurrentUserDetailsHandler(BaseRequestHandler):
    #todo: new global function for getting the current user
    def get(self):
        current_logged_in_user = users.get_current_user()
        if current_logged_in_user is not None:
            employee_query = model.Employee.query().filter(model.Employee.email == current_logged_in_user.email())
            query_result = employee_query.get()
            if query_result is not None:
                response_module.give_response(self, query_result.details())
            else:
                print "Persoon bestaat niet"
                self.abort(500)
        else:
            print "NIET ingelogd"
            self.abort(500)


class UserSettingsHandler(BaseRequestHandler):
    def get(self):
        employee = get_current_person(self)
        if employee is not None:
            response_module.give_response(self,
                                          json.dumps(employee.details()))
        #TODO what to do when employee is None?

    def put(self):
        employee = get_current_person(self)
        if employee is not None:
            employee.wants_email_notifications = bool(self.request.get("wants_email_notifications"))
            employee.wants_phone_notifications = bool(self.request.get("wants_phone_notifications"))
        #TODO what to do when employee is None?

application = webapp.WSGIApplication(
    [
        ('/persons', AllPersonsHandler),
        ('/persons/(.*)', SpecificPersonHandler),
        ('/user/settings/', UserSettingsHandler),
        ('/details/', CurrentUserDetailsHandler),
        ('/employees', AllEmployeesHandler),
        ('/employees/details/(.*)', SpecificEmployeeDetailsHandler),
        ('/employees/(.*)', SpecificEmployeeHandler),
        ('/open_declarations/employee', AllOpenDeclarationsForEmployeeHandler),
        ('/current_user_details/', CurrentUserDetailsHandler),
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
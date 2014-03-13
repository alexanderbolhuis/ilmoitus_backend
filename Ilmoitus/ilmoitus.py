__author__ = 'Sjors van Lemmen'
import webapp2 as webapp
import response_module
import model
import json
from google.appengine.api import users


def get_current_employee(self):
    current_logged_in_user = users.get_current_user()
    if current_logged_in_user is not None:
        employee_query = model.Person.query().filter(model.Employee.email == current_logged_in_user.email())
        query_result = employee_query.get()
        if query_result is not None:
            return query_result
        else:
            return False
    else:
        return False


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
                                                                model.Person,  # an HTTP response
                                                                self.get_header_limit(),
                                                                self.get_header_offset())


class SpecificPersonHandler(BaseRequestHandler):
    def get(self, person_id):
        response_module.respond_with_object_by_id(self,
                                                  model.Employee,
                                                  person_id)  # Since NDB, keynames are also valid ID's!


class AllEmployeesHandler(BaseRequestHandler):
    def get(self):
        response_module.respond_with_object_collection_by_class(self,
                                                                model.Employee,  # Will only get Employees or subclasses
                                                                self.get_header_limit(),
                                                                self.get_header_offset())


class SpecificEmployeeHandler(BaseRequestHandler):
    def get(self, employee_id):
        response_module.respond_with_object_by_id(self,
                                                  model.Employee,
                                                  employee_id)


class AuthorizationStatusHandler(BaseRequestHandler):
    def get(self):
        person = get_current_employee(self)
        if person is not False:  # TODO: update this to a lookup in the dict instead of a boolean check
            #Create a default data dictionary to limit code duplication
            response_data = {"person_id": person.key.integer_id(), "is_logged_in": True,
                             "is_application_admin": users.is_current_user_admin()}
            response_module.give_response(self, json.dumps(response_data))
        else:
            #Person is either not logged in, or not known in the application's model
            response_module.give_response(self, json.dumps({"is_logged_in": False}))


class LoginHandler(BaseRequestHandler):
    def get(self):
        person = get_current_employee(self)
        if person is False:  # TODO: update this to a lookup in the dict instead of a boolean check
            self.redirect(users.create_login_url('/auth/login'))
            # We will return to the same url after logging in since this handler will than check if the login
            # was really successful, and automatically redirect to the main page if so.
        else:
            #TODO: redirect here to the actual "main" page
            #TODO: research/discuss how to make this work cross platform (how will iOS & Android handle redirects?)
            self.redirect("/main_page")


class LogoutHandler(BaseRequestHandler):
    def get(self):
        person = get_current_employee(self)
        if person is not False:  # TODO: update this to a lookup in the dict instead of a boolean check
            self.redirect(users.create_logout_url('/auth/logout/'))
            # We will return to the same url after logging out since this handler will than check if the login
            # was really successful, and automatically redirect to the login page if so.
        else:
            #TODO: redirect here to the actual login page
            #TODO: research/discuss how to make this work cross platform (how will iOS & Android handle redirects?)
            self.redirect("/login_page")


class SpecificEmployeeDetailsHandler(BaseRequestHandler):
    def get(self, employee_id):
        response_module.respond_with_object_details_by_id(self,
                                                          model.Employee,
                                                          employee_id)


class UserSettingsHandler(BaseRequestHandler):
    def get(self, user_id):
        employee = model.Employee.get_by_id(long(user_id))
        if employee is not None:
            response_module.give_response(self,
                                          json.dumps(employee.details()))
        #TODO what to do when employee is None?



application = webapp.WSGIApplication(
    [
        ('/persons', AllPersonsHandler),
        ('/persons/(.*)', SpecificPersonHandler),
        ('/user/settings/(.*)', UserSettingsHandler),
        ('/employees', AllEmployeesHandler),
        ('/employees/(.*)', SpecificEmployeeHandler),
        ('/employees/details/(.*)', SpecificEmployeeDetailsHandler),
        ('/auth/login/(.*)', LoginHandler),
        ('/auth/logout/(.*)', LogoutHandler),
        ('/auth/(.*)', AuthorizationStatusHandler),  # needs to be bellow other auth handlers!
        ('.*', DefaultHandler)
    ],
    debug=True)  # if debug is set to false,
# any uncaught exceptions will only trigger a server error without any details
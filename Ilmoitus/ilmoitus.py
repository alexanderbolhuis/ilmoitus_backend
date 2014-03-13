__author__ = 'Sjors van Lemmen'
import webapp2 as webapp
import response_module
import model
import json
from google.appengine.api import users


def get_current_employee(self):
    current_logged_in_user = users.get_current_user()
    if current_logged_in_user is not None:
        employee_query = model.Employee.query().filter(model.Employee.email == current_logged_in_user.email())
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
        response_module.respond_with_object_details_by_id(self,
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
        response_module.respond_with_object_details_by_id(self,
                                                          model.Employee,
                                                          employee_id)


class AuthorizationStatusHandler(BaseRequestHandler):
    def get(self, user_id):
        safe_id = 0
        try:
            safe_id = int(user_id)
        except ValueError:
            #TODO: error messages;
            # the given user id was of an invalid format; request could not be handled
            self.abort(400)

        person = model.Person.get_by_id(safe_id)
        #Create a default data dictionary to limit code duplication
        response_data = {"id": user_id, "is_logged_in": False,
                         "is_application_admin": False}
        if person is not None:
            user = users.get_current_user()
            if user is not None:
                if user.email() == person.email:  # One can only ask status on him/herself!
                    response_data["is_logged_in"] = True
                    response_data["is_application_admin"] = users.is_current_user_admin()
                    response_module.give_response(self, json.dumps(response_data))
                else:
                    #TODO: error messages;
                    # the request attempted to retrieve the status of someone else, which is illegal
                    self.abort(500)
            else:
                #Requested user was not logged in, which makes it impossible to check if
                #   a. The id of the requested user belonged to the logged in user (since there is none)
                #   b. The id of the requested user belonged to an admin account
                #      (since we don't know what Google account belongs to the account)
                response_data["is_application_admin"] = "unknown"
                response_module.give_response(self, json.dumps(response_data))
        else:
            #TODO: error messages;
            #Person is not known in the application
            self.abort(404)


class LoginHandler(BaseRequestHandler):
    def get(self, user_id):
        user = users.get_current_user()
        if user is None:
            self.redirect(users.create_login_url('/auth/login/' + str(user_id)))
            # We will return to the same url after logging in since this handler will than check if the login
            # was really successful, and automatically redirect to the main page if so.
        else:
            #TODO: redirect here to the actual "main" page
            #TODO: research/discuss how to make this work cross platform (how will iOS & Android handle redirects?)
            self.redirect("/main_page")


class LogoutHandler(BaseRequestHandler):
    def get(self, user_id):
        user = users.get_current_user()
        if user is not None:
            self.redirect(users.create_logout_url('/auth/logout/' + str(user_id)))
            # We will return to the same url after logging out since this handler will than check if the login
            # was really successful, and automatically redirect to the login page if so.
        else:
            #TODO: redirect here to the actual login page
            #TODO: research/discuss how to make this work cross platform (how will iOS & Android handle redirects?)
            self.redirect("/login_page")


application = webapp.WSGIApplication(
    [
        ('/persons', AllPersonsHandler),
        ('/persons/(.*)', SpecificPersonHandler),
        ('/employees', AllEmployeesHandler),
        ('/employees/(.*)', SpecificEmployeeHandler),
        ('/auth/login/(.*)', LoginHandler),
        ('/auth/logout/(.*)', LogoutHandler),
        ('/auth/(.*)', AuthorizationStatusHandler),  # needs to be bellow other auth handlers!
        ('.*', DefaultHandler)
    ],
    debug=True)  # if debug is set to false,
# any uncaught exceptions will only trigger a server error without any details
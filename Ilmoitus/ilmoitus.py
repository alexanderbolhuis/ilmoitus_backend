__author__ = 'Sjors van Lemmen'
import webapp2 as webapp
import response_module
import model
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


application = webapp.WSGIApplication(
    [
        ('/persons', AllPersonsHandler),
        ('/persons/(.*)', SpecificPersonHandler),
        ('/employees', AllEmployeesHandler),
        ('/employees/(.*)', SpecificEmployeeHandler),
        ('.*', DefaultHandler)
    ],
    debug=True)  # if debug is set to false,
# any uncaught exceptions will only trigger a server error without any details
__author__ = 'Sjors van Lemmen'

from response_module import *
from ilmoitus_model import *
from handlers.declaration_list import *
from handlers.declaration_handler import *
from handlers.employee_list import *
from handlers.declaration_type_list import *
from handlers.currentuser_handler import *
from ilmoitus_auth import *
import data_bootstrapper
import webapp2 as webapp


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
        give_hard_response(self, html_data)


application = webapp.WSGIApplication(
    [
        #Current user handlers
        ('/current_user/details', CurrentUserDetailsHandler),
        ('/current_user/settings', CurrentUserSettingsHandler),
        ('/current_user/supervisors', CurrentUserSupervisorsHandler),
        ('/current_user/declarations', AllDeclarationsForEmployeeHandler),
        ('/current_user/declarations/assigned', AllDeclarationsForSupervisorHandler),
        ('/current_user/declarations/assigned_history', AllHistoryDeclarationsForSupervisorHandler),

        #Employee handlers
        ('/employees', AllEmployeesHandler),
        ('/employee_summary', SupervisorEmployeeTotalHandler),
        ('/employee/(.*)/total_declarations', SpecificEmployeeTotalDeclarationsHandler),
        ('/employee/(.*)', SpecificEmployeeDetailsHandler),

        #Declaration list
        ('/declarations/hr', AllDeclarationsForHumanResourcesHandler),
        ('/declarations/hr_history', AllHistoryDeclarationsForHumanResourcesHandler),

        #Declaration type list
        ('/declarationtypes', AllDeclarationTypesHandler),
        ('/declarationtype/(.*)', AllDeclarationTypeSubTypeHandler),
        ('/declarationsubtypes', AllDeclarationSubTypesHandler),

        #Declaration handlers
        ('/declaration/(.*)/lock', OpenToLockedDeclarationHandler),
        ('/declaration/(.*)/forward_to_supervisor', ForwardDeclarationHandler),
        ('/declaration/(.*)/decline_by_supervisor', DeclineBySupervisorHandler),
        ('/declaration/(.*)/approve_by_supervisor', ApproveBySupervisorHandler),
        ('/declaration/(.*)/decline_by_hr', DeclineByHumanResourcesHandler),
        ('/declaration/(.*)/approve_by_hr', ApproveByHumanResourcesHandler),
        ('/declaration/(.*)', SpecificDeclarationHandler),
        ("/declaration", NewDeclarationHandler),

        #Attchment handlers
        ('/attachment/(.*)/(.*)', SpecificAttachmentHandler),
        ('/attachment_token/(.*)', CreateAttachmentTokenHandler),

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
    debug=True)
# if debug is set to false,
# any uncaught exceptions will only trigger a server error without any details
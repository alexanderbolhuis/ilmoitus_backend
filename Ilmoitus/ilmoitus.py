__author__ = 'Sjors van Lemmen'
import webapp2 as webapp
import response_module
import ilmoitus_model
import json
import datetime
import dateutil.parser
import data_bootstrapper
import logging
from google.appengine.api import users
from google.appengine.ext import ndb
from error_response_module import give_error_response
import mail_module
import ilmoitus_auth


class BaseRequestHandler(webapp.RequestHandler):
    """
    Wrapper class that will allow all other handler classes to make easily read what the
    limit and/or offset is for a request
    """
    def options(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE'

    def get_header(self, key):
        header = self.request.get(key, default_value=None)
        return header

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
        result = ilmoitus_auth.get_current_person(self)

        if result["user_is_logged_in"]:
            person = result["person_value"]

            #Create a default data dictionary to limit code duplication
            response_data = {"person_id": person.key.integer_id(), "is_logged_in": True,
                             "is_application_admin": users.is_current_user_admin() }
            response_module.give_response(self, json.dumps(response_data))
        else:
            #Person is not known in the application's model
            response_module.give_response(self, json.dumps({"is_logged_in": False}))


class LoginHandler(BaseRequestHandler):
    def post(self):
        result = ilmoitus_auth.authencate(self.request.POST["email"], self.request.POST["password"])

        if result["passed"]:
            person = result["person_value"]

            response_data = {"person_id": person.key.integer_id(), "is_logged_in": True,
                             "is_application_admin": users.is_current_user_admin(), "token":result["token"] }
            response_module.give_response(self, json.dumps(response_data))
        else:
            response_module.give_response(self, json.dumps({"is_logged_in": False}))


class AllDeclarationsForEmployeeHandler(BaseRequestHandler):
    def get(self):
        #model.Employee as param since this handler handles calls from their POV.
        person_data = ilmoitus_auth.get_current_person(self, "employee")
        person = person_data["person_value"]

        if person is not None:
            declaration_query = ilmoitus_model.Declaration.query(ilmoitus_model.Declaration.created_by == person.key)

            query_result = declaration_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            response_module.respond_with_existing_model_object_collection(self, query_result)
        else:
            give_error_response(self, 401, "De declaraties kunnen niet opgehaald worden omdat u niet de juiste"
                                           " permissies heeft.", "current_user is None")


class SpecificEmployeeDetailsHandler(BaseRequestHandler):
    def get(self, employee_id):
        response_module.respond_with_object_details_by_id(self,
                                                          ilmoitus_model.Person,
                                                          employee_id)


class AllDeclarationsForSupervisor(BaseRequestHandler):
    def get(self):
        person_data = ilmoitus_auth.get_current_person(self, "supervisor")
        person = person_data["person_value"]

        if person is not None and person.class_name == 'supervisor':

            declaration_query = ilmoitus_model.Declaration.query(
                ilmoitus_model.Declaration.class_name == 'open_declaration',
                ilmoitus_model.Declaration.assigned_to == person.key)
            query_result = declaration_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            response_module.respond_with_existing_model_object_collection(self, query_result)
        else:
            give_error_response(self, 401, "De declaraties voor leidinggevenden kunnen niet opgehaald worden omdat u"
                                           " niet de juiste permissies heeft.", "current_user is None or not a supervisor")


class CurrentUserDetailsHandler(BaseRequestHandler):
    def get(self):
        current_user_data = ilmoitus_auth.get_current_person(self)
        user_is_logged_in = current_user_data["user_is_logged_in"]
        if user_is_logged_in is True:
            current_user = current_user_data["person_value"]
            if current_user is not None:
                response_module.give_response(self, current_user.get_object_json_data())
            else:
                give_error_response(self, 404, "De ingelogde gebruiker is niet in het systeem gevonden!",
                                    "current_user is None")
        else:
            give_error_response(self, 401, "De huidige user details kunnen niet opgehaald worden omdat u daar niet de "
                                           "juiste permissies voor heeft.", "user_is_logged_in is False")


class UserSettingsHandler(BaseRequestHandler):
    def get(self):
        employee = ilmoitus_auth.get_current_person(self)
        if employee is not None:
            response_module.give_response(self, json.dumps(employee.details()))
            response_module.give_response(self, employee.get_object_json_data())
            #TODO what to do when employee is None?

    def put(self):
        employee = ilmoitus_auth.get_current_person(self)
        if employee is not None:
            employee.wants_email_notifications = bool(self.request.get("wants_email_notifications"))
            employee.wants_phone_notifications = bool(self.request.get("wants_phone_notifications"))
            #TODO what to do when employee is None?


class SetLockedToSupervisorApprovedDeclarationHandler(BaseRequestHandler):
    def put(self):
        #Only supervisors can perform the actions in this handler: check for that first
        current_person_data = ilmoitus_auth.get_current_person(self, "supervisor")
        if "user_is_logged_in" not in current_person_data.keys() or \
                not current_person_data["user_is_logged_in"]:  # if logged in is false
            give_error_response(self, 401, "Kan de declaratie niet goedkeuren. U bent niet ingelogd.",
                                "get_current_person returned a False value for user_is_logged_in")

        current_person_object = current_person_data["person_value"]
        if current_person_object is None:
            give_error_response(self, 401, "U bent niet bekend binnen het systeem"
                                           " of u heeft niet de rechten van een"
                                           " leidinggevende.",
                                "person_value key in get_current_person was None")
        declaration_data = None
        try:
            declaration_data = json.loads(self.request.body)
        except ValueError:
            if self.request.body is None or len(self.request.body) <= 0:
                give_error_response(self, 400, "Kan de declaratie niet goedkeuren. Er is geen declaratie opgegeven "
                                               "om goed te keuren.",
                                    "Request body was None.")
        if declaration_data is None or not isinstance(declaration_data, dict):
            give_error_response(self, 400, "Kan de declaratie niet goedkeuren. Er is geen declaratie opgegeven "
                                           "om goed te keuren.",
                                "Request.body did not contain valid json data")

        declaration_id = None
        try:
            declaration_id = long(declaration_data["id"])
        except KeyError:
            give_error_response(self, 400, "Kan de declaratie niet goedkeuren. De opgegeven data bevat geen "
                                           "identificatie voor een declaratie.",
                                "The body doesn't contain an ID key.")
        except (TypeError, ValueError):
            give_error_response(self, 400, "Kan de declaratie niet goedkeuren. De opgegeven data bevat een "
                                           "ongeldige identificatie voor een declaratie.",
                                "Failed to parse the value of the ID key in the body to a long.")

        declaration_object = ilmoitus_model.Declaration.get_by_id(declaration_id)
        try:
            if current_person_object.key not in declaration_object.assigned_to:
                give_error_response(self, 401, "Kan de declaratie niet goedkeuren. Deze declaratie is niet aan "
                                               "u toegewezen",
                                    "current_person_object's id was not in the declaration_object's asigned_to list.")

            if declaration_object.class_name != "locked_declaration":
                give_error_response(self, 422, "Kan de declaratie niet goedkeuren. De opgegeven declaratie is niet "
                                               "gesloten en kan dus niet goedgekeurd worden.",
                                    "Class name of fetched object was not equal locked_declaration")

            if declaration_object.items_total_price > current_person_object.max_declaration_price and current_person_object.max_declaration_price != -1:
                give_error_response(self, 401, "De huidige persoon mag deze declaratie niet goedkeuren. Bedrag te hoog.",
                                    "Total item costs is: " + str(declaration_object.items_total_price) + " and the max amount is: "
                                    + str(current_person_object.max_declaration_price) + " .")

            declaration_object.class_name = "supervisor_approved_declaration"
            declaration_object.submitted_to_human_resources_by = current_person_object.key
            declaration_object.supervisor_approved_at = datetime.datetime.now()
            if "supervisor_comment" in declaration_data.keys():
                #No need to check if the string parsing could fail here; json will always have data that
                #can be parsed to a string
                declaration_object.supervisor_comment = str(declaration_data["supervisor_comment"])

        except AttributeError:
            give_error_response(self, 404, "Kan de declaratie niet goedkeuren. De opgegeven identificatie is "
                                           "onbekend.",
                                "Query result from the value of the ID key of the body returned None.")
        declaration_object.put()
        mail_module.send_message_declaration_status_changed(self, declaration_object)
        response_module.give_response(self, json.dumps(declaration_object.get_object_as_data_dict()))


class CurrentUserSupervisors(BaseRequestHandler):
    def get(self):
        #TODO now this function gets all supervisors, we need to know if it only need supervisors of current person
        current_user_data = ilmoitus_auth.get_current_person(self)
        user_is_logged_in = current_user_data["user_is_logged_in"]
        if user_is_logged_in is True:
            supervisor_query = ilmoitus_model.Person.query(ilmoitus_model.Person.class_name == "supervisor")
            query_result = supervisor_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

            response_module.respond_with_existing_model_object_collection(self, query_result)
        else:
            give_error_response(self, 401, "Kan geen leidinggevenden ophalen omdat u hier niet de juiste "
                                           "permissies voor heeft.",
                                "current_user is None")


class AllDeclarationsForHumanResourcesHandler(BaseRequestHandler):
    def get(self):
        person_data = ilmoitus_auth.get_current_person(self, "human_resources")
        person = person_data["person_value"]
        if person is not None:
            if person.class_name == "human_resources":  # person.key.class_name == "human_resources":
                declaration_query = ilmoitus_model.Declaration.query(
                    ilmoitus_model.Declaration.class_name == "supervisor_approved_declaration")

                query_result = declaration_query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())

                response_module.respond_with_existing_model_object_collection(self, query_result)
            else:
                give_error_response(self, 401, "De declaraties kunnen niet worden opgehaald omdat u niet "
                                               "de juiste permissies heeft.",
                                    "current_user not from human_resources")
        else:
            give_error_response(self, 401, "De declaraties kunnen niet worden opgehaald omdat u niet "
                                           "de juiste permissies heeft.",
                                "current_user is None")


class CurrentUserAssociatedDeclarations(BaseRequestHandler):
    def get(self):
        person_data = ilmoitus_auth.get_current_person(self)
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
            give_error_response(self, 404, "De declaraties kunnen niet worden opgehaald omdat er geen declaraties"
                                           "zijn gevonden die aan u zijn geassocieerd.",
                                "query_result is empty")


class AddNewDeclarationHandler(BaseRequestHandler):
    def post(self):
        # Check if logged in
        current_person_data = ilmoitus_auth.get_current_person(self, "employee")
        if "user_is_logged_in" not in current_person_data.keys() or \
                not current_person_data["user_is_logged_in"]:
            give_error_response(self, 401,
                                "Er is niemand ingelogd.",
                                "get_current_person returned a False value for user_is_logged_in")
        # Check if body is set
        post_data = None
        try:
            post_data = json.loads(self.request.body)
        except ValueError:
            if self.request.body is None or len(self.request.body) <= 0:
                give_error_response(self, 400, "Er is geen declaratie opgegeven om aan te maken.",
                                    "Request body was None.")

        if post_data is None:
            give_error_response(self, 400, "Er is geen declaratie opgegeven om aan te maken.",
                                "Request.body did not contain valid json data")

        # Check if body contains declaration data
        declaration_data = None
        try:
            declaration_data = post_data["declaration"]
        except ValueError:
            give_error_response(self, 400, "Er is geen declaratie opgegeven om aan te maken.",
                                    "Request body was None.")

        # Check if body contains declarationlines
        declarationlines_data = None
        try:
            declarationlines_data = post_data["lines"]
        except ValueError:
            give_error_response(self, 400, "Er zijn geen declaratieitems opgegeven om aan te maken.",
                                    "Request body was None.")

        # Check if declaration has owner and assigned to values (mandatory)
        try:
            created_by = declaration_data["created_by"]
            assigned_to = declaration_data["assigned_to"][0]
        except Exception:
            give_error_response(self, 400, "De opgegeven data mist waardes voor een declaratie.",
                                "The body misses keys.")

        # Check if created_by is a valid user
        try:
            created_by = ilmoitus_model.Person.get_by_id(int(created_by))
        except Exception:
            give_error_response(self, 400, "De maker is niet bekent in het systeem.",
                                "The owner is unknown.")

        # Check if created_by is logged_in
        logged_in_person = ilmoitus_auth.get_current_person(self)
        if created_by.key != logged_in_person["person_value"].key:
            give_error_response(self, 400, "De maker is niet ingelogd in het systeem.",
                                "The owner is not logged in.")

        # Check if assigned_to is a valid user
        try:
            assigned_to = ilmoitus_model.Person.get_by_id(int(assigned_to))
        except Exception:
            give_error_response(self, 400, "De supervisor is niet bekent in het systeem.",
                                "The supervisor is unknown.")

        # Check if assigned_to is a supervisor
        if assigned_to.class_name != "supervisor":
            give_error_response(self, 400, "De supervisor is niet bekent in het systeem.",
                                "The supervisor is unknown.")

        # Check if each declarationline has a receipt_date, a cost, and a declaration_sub_type
        try:
            for line in declarationlines_data:
                line["receipt_date"]
                line["cost"]
                line["declaration_sub_type"]
        except Exception:
            give_error_response(self, 400, "De opgegeven data mist waardes voor een declaratieline.",
                                "The body misses keys.")

        # Check if declaration subtypes exist
        for line in declarationlines_data:
            sub_type = ilmoitus_model.DeclarationSubType.get_by_id(int(line["declaration_sub_type"]))
            if sub_type is None:
                give_error_response(self, 400, "De declaratie_sub_type bestaat niet.",
                                    "The declaration_sub_type is unknown.")

        if "attachments" in post_data:
            try:
                for attachment_data in post_data["attachments"]:
                    attachment_data["name"]
                    attachment_data["file"]
            except KeyError:
                give_error_response(self, 400, "Kan geen declaratie toevoegen. De opgestuurde bijlage gegevens "
                                               "kloppen niet.",
                                    "The body misses keys at an attachment.")

            for attachment_data in post_data["attachments"]:
                data = attachment_data["file"].split(":")[0]
                mime = attachment_data["file"].split(":")[1].split(";")[0]
                base = attachment_data["file"].split(":")[1].split(";")[1].split(",")[0]

                if data != "data" or base != "base64":
                    give_error_response(self, 400, "Kan geen declaratie toevoegen. De opgestuurde bijlage gegevens "
                                                       "kloppen niet.",
                                        "The base64 string is incorrect.")

                if mime != "application/pdf" and mime.split("/")[0] != "image":
                    give_error_response(self, 400, "Kan geen declaratie toevoegen. Alleen pdf's of images zijn toegestaan.",
                                        "MimeType does not equal application/pdf or image/*", more_info=mime)

        # Post declaration
        declaration = ilmoitus_model.Declaration()
        declaration.class_name = "open_declaration"
        declaration.assigned_to = [assigned_to.key]
        declaration.created_by = created_by.key
        declaration.comment = declaration_data["comment"]
        declaration.items_count = 0
        declaration.items_total_price = 0
        declaration.put()

        posted_lines = []
        # Post declarationlines
        for line in declarationlines_data:
            newline = ilmoitus_model.DeclarationLine()
            newline.declaration = declaration.key

            try:
                newline.cost = int(line["cost"])
                declaration.items_count += 1
                declaration.items_total_price += newline.cost
            except Exception:
                give_error_response(self, 400, "De opgegeven data bevat foute waardes voor een declaratieline.",
                                "The body contains wrong values.")

            newline.receipt_date = dateutil.parser.parse(line["receipt_date"])
            newline.declaration_sub_type = ilmoitus_model.DeclarationSubType.get_by_id(int(line["declaration_sub_type"])).key
            newline.put()
            posted_lines.append(newline)

        declaration.put()

        posted_attachments = []
        if "attachments" in post_data:
            try:
                for attachment_data in post_data["attachments"]:
                    attachment = ilmoitus_model.Attachment()
                    attachment.declaration = declaration.key
                    attachment.name = attachment_data["name"]
                    attachment.file = attachment_data["file"]
                    attachment.put()
                    posted_attachments.append(attachment.get_object_as_data_dict())
            except Exception:
                give_error_response(self, 400, "Kan geen declaratie toevoegen. De opgestuurde data bevat foute "
                                               "waardes voor een bijlage.",
                                    "The body contains wrong values.")


        lines = map(lambda declaration_line: declaration_line.get_object_as_data_dict(), posted_lines)
        combined_dict = json.dumps({'declaration': declaration.get_object_as_data_dict(),
                                    'lines': lines,
                                    'attachments': posted_attachments})

        response_module.give_response(self, combined_dict)


class SpecificDeclarationHandler(BaseRequestHandler):
    def get(self, declaration_id):
        person_data = ilmoitus_auth.get_current_person(self)
        current_user = person_data["person_value"]

        if current_user is None:
            give_error_response(self, 401, "There is no user logged in", None, 401)

        # checks if declaration_id is of type int
        if str.isdigit(declaration_id):

            key = current_user.key
            result = ilmoitus_model.Declaration.get_by_id(long(declaration_id))

            if result is None:
                give_error_response(self, 404, "Kan de opgevraagde declaratie niet vinden",
                                    "Declaration id can only be of the type integer and cannot be None", 404)

            if result.created_by == key:
                response_module.give_response(self, result.get_object_json_data())

            elif current_user.class_name == 'supervisor':
                if key in result.assigned_to:
                    response_module.give_response(self, result.get_object_json_data())
                else:
                    give_error_response(self, 401,
                                        "Deze declratie is niet aan jouw toegewezen", None, 401)

            elif current_user.class_name == 'human_resources' and result.class_name == \
                    'supervisor_approved_declaration' and result.submitted_to_human_resources_by is not None:
                response_module.give_response(self, result.get_object_json_data())
            else:
                give_error_response(self, 401,
                                    "Je hebt niet de juiste rechten op deze declratie te openen", None, 401)
        # if declaration_id not is int
        else:
            give_error_response(self, 400, "Kan de opgevraagde declaratie niet vinden",
                                "Declaration id can only be of the type integer and cannot be None", 400)


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

            query = ilmoitus_model.Attachment.query(ilmoitus_model.Attachment.declaration == declaration.key)
            attachments = query.fetch(limit=self.get_header_limit(), offset=self.get_header_offset())
            if attachments is None:
                    give_error_response(self, 404, "De declaratie heeft geen bijlagen.",
                                        "No attachments with the specified declaration_id in the database.", 404)
        else:
            give_error_response(self, 400, "Kan geen bijlagen ophalen.",
                                "attachment id can only be of the type integer.", 404)

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
                                        "attachment id does not exist in the database.", 404)
        else:
            give_error_response(self, 400, "Kan de opgevraagde bijlage niet vinden.",
                                "attachment id can only be of the type integer.", 404)

        response_module.give_response(self, attachment.get_object_json_data())


class ApproveByHumanResources(BaseRequestHandler):
    def put(self):
        person_data = ilmoitus_auth.get_current_person(self, "human_resources")
        current_user = person_data["person_value"]

        if current_user is not None:
            if self.request.body is not None:
                data = None
                try:
                    data = json.loads(self.request.body)
                except ValueError:
                    give_error_response(self, 500, "Kan de declaratie niet goedkeuren omdat er ongeldige data "
                                                   "is verstuurd.",
                                        "Invalid JSON data; invalid format.", more_info=str(self.request.body))

                declaration_id = data["id"]
                pay_date = dateutil.parser.parse(data["pay_date"])
                today_date = datetime.datetime.now()

                declaration = ilmoitus_model.Declaration.get_by_id(declaration_id)

                if declaration.class_name == "supervisor_approved_declaration":
                    declaration.class_name = "human_resources_approved_declaration"
                    declaration.human_resources_approved_at = today_date
                    declaration.will_be_payed_out_on = pay_date
                    declaration.human_resources_approved_by = current_user.key
                    declaration.put()
                    mail_module.send_mail_declaration_approved(self, declaration)
                    response_module.give_response(self, declaration.get_object_json_data())
                else:
                    give_error_response(self, 500, "Kan de declaratie niet goedkeuren omdat deze niet eerst "
                                                   "door een leidinggevende is goedgekeurd.",
                                        "Can only approve a supervisor_approved_declaration.")
            else:
                give_error_response(self, 500, "Kan de declaratie niet goedkeuren omdat er is geen data is opgegeven.",
                                    "Request body is None.")
        else:
            #user does not have the appropriate permissions or isn't logged in at all.
            give_error_response(self, 401, "Geen permissie om een declaratie goed te keuren!",
                                "current_user is None or not from human_resources")


class SupervisorDeclarationToHrDeclinedDeclarationHandler(BaseRequestHandler):
    def put(self):
        person_data = ilmoitus_auth.get_current_person(self, "human_resources")
        person = person_data["person_value"]
        if person is not None:
            if person.class_name == "human_resources":  # person.key.class_name == "human_resources":
                if self.request.body is not None:
                    data = None
                    try:
                        data = json.loads(self.request.body)
                    except ValueError:
                        give_error_response(self, 500, "Kan de declaratie niet afkeuren omdat er ongeldige data "
                                                       "is verstuurd",
                                            "Invalid json data; Invalid format", more_info=str(self.request.body))
                    declaration_id = data['declaration_id']
                    person_key = person.key
                    current_date = datetime.datetime.now()
                    declaration = ilmoitus_model.Declaration.get_by_id(declaration_id)
                    if declaration.class_name == 'supervisor_approved_declaration':
                        declaration.class_name = 'human_resources_declined_declaration'
                        declaration.human_resources_declined_by = person_key
                        declaration.human_resources_declined_at = current_date
                        declaration.put()
                        mail_module.send_message_declaration_status_changed(self, declaration)
                        response_module.give_response(self, declaration.get_object_json_data())
                    else:
                        #
                        give_error_response(self, 500, "Kan de declaratie niet afkeuren omdat deze niet eerst "
                                                       "door een leidinggevende is goedgekeurd.",
                                            "Can only decline a supervisor_approved_declaration.")
                else:
                    #
                    give_error_response(self, 500, "Kan de declaratie niet afkeuren omdat er is geen data is "
                                                   "opgegeven.",
                                        "Request body is None!.")
            else:
                give_error_response(self, 401, "Kan de declaratie niet afkeuren omdat u niet de juiste "
                                               "permissie heeft.",
                                    "current_user is not from human_resources")
        else:
            give_error_response(self, 401, "Kan de declaratie niet afkeuren omdat u niet ingelogd bent.",
                                "current_user is None")


class SetOpenToLockedDeclaration(BaseRequestHandler):
    def put(self):
        person_data = ilmoitus_auth.get_current_person(self, "supervisor")
        current_user = person_data["person_value"]

        if current_user is not None:
            if self.request.body is not None:
                data = None
                try:
                    data = json.loads(self.request.body)
                except ValueError:
                    give_error_response(self, 500, "Er is ongeldige data verstuurd; kan het verzoek niet afhandelen",
                                        "Invalid JSON data; invalid format.", more_info=str(self.request.body))

                declaration_id = long(data["id"])

                today_date = datetime.datetime.now()

                declaration = ilmoitus_model.Declaration.get_by_id(declaration_id)

                if declaration.class_name == "open_declaration":
                    declaration.class_name = "locked_declaration"
                    declaration.locked_at = today_date
                    declaration.put()
                    response_module.give_response(self, declaration.get_object_json_data())
                else:
                    give_error_response(self, 500, "Moet een open declaration zijn",
                                        "Can only lock a open declaration.")
            else:
                give_error_response(self, 500, "Er is geen data opgegeven.",
                                    "Request body is None.")
        else:
            #user does not have the appropriate permissions or isn't logged in at all.
            give_error_response(self, 401, "Geen permissie om een declaratie te locken!",
                                    "No premissions for locking a declaration")


class SpecificEmployeeTotalDeclarationsHandler(BaseRequestHandler):
    def get(self, employee_id):
        # Only supervisors can perform the actions in this handler: check for that first
        current_person_data = ilmoitus_auth.get_current_person(self, "Supervisor")
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
        ('/declaration/approve_by_hr', ApproveByHumanResources),
        ('/persons', AllPersonsHandler),
        ('/persons/(.*)', SpecificPersonHandler),
        ('/user/settings/', UserSettingsHandler),
        ('/employees', AllEmployeesHandler),
        ('/employees/details/(.*)', SpecificEmployeeDetailsHandler),
        ('/employees/total_declarations/(.*)', SpecificEmployeeTotalDeclarationsHandler),
        ('/employees/(.*)', SpecificEmployeeHandler),
        ('/declarations/hr', AllDeclarationsForHumanResourcesHandler),
        ('/declaration/declined_by_hr', SupervisorDeclarationToHrDeclinedDeclarationHandler),
        ('/supervisors/', CurrentUserSupervisors),
        ('/declarations/employee', AllDeclarationsForEmployeeHandler),
        ('/current_user/associated_declarations', CurrentUserAssociatedDeclarations),
        ('/current_user/details', CurrentUserDetailsHandler),
        ('/declarations/supervisor', AllDeclarationsForSupervisor),
        ('/declaration/(.*)', SpecificDeclarationHandler),
        ('/declaration/attachments/(.*)', SpecificDeclarationAttachmentsHandler),
        ('/attachment/(.*)', SpecificAttachmentHandler),
        ('/declarations/approve_locked', SetLockedToSupervisorApprovedDeclarationHandler),
        ('/declaration/lock', SetOpenToLockedDeclaration),
        ("/declaration", AddNewDeclarationHandler),
        ('/auth/login', LoginHandler),
        ('/auth', AuthorizationStatusHandler),
        ('/clear', data_bootstrapper.ClearHandler),
        ('/fill', data_bootstrapper.FillHandler),
        ('/create', data_bootstrapper.CreateDataHandler),
        ('.*', DefaultHandler)
    ],
    debug=True)  # if debug is set to false,
# any uncaught exceptions will only trigger a server error without any details
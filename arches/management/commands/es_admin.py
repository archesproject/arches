from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings
import urllib3.request, urllib3.response
import json
import re

# Management command to administer the Elasticsearch security preferences. Provides the following functionality:
# 1. create, update, delete and list a role for each application that has minimal privileges necessary
# 2. create, update and delete a user with a single role as created in 1
# 3. creates, delete and list an API Key to be stored in the application settings

class Command(BaseCommand):
    # Parameters used to connect to the Elasticsearch instance
    es_connection_parameters = {
        "host": settings.ELASTICSEARCH_HTTP_HOST,
        "port": settings.ELASTICSEARCH_HTTP_PORT,
        "cert_location":  settings.ELASTICSEARCH_CERT_LOCATION,
        "username": None,
        "password": None
    }

    endpoints = {
        "get_roles": {"mode": "GET", "path": "_security/role"},
        "get_role": {"mode": "GET", "path": "_security/role/%(role_name)s"},
        "create_role": {"mode": "PUT", "path": "_security/role/%(role_name)s", "payload": """
        {
          "cluster": ["manage_own_api_key"],
          "applications": [
            {
              "application": "%(app_name)s",
              "privileges": [ "read", "write" ],
              "resources": [ "*" ]
            }
          ],
          "indices": [
          {
            "names": ["%(app_name)s_*"],
            "privileges": ["create_index", "delete_index", "write"]
          }
          ], "metadata": {
            "application": ["%(app_name)s"],
            "description": ["Application owner role for the %(app_name)s application"]
          }
        }"""},
        "delete_role": {"mode": "DELETE", "path": "_security/role/%(role_name)s"},


        "get_users": {"mode": "GET", "path": "_security/user"},
        "get_user": {"mode": "GET", "path": "_security/user/%(app_name)s"},
        "create_user": {"mode": "PUT", "path": "_security/user/%(app_name)s", "payload": """
        { "password" : "%(password)s",
           "roles" : [ "%(app_name)s-user" ], "full_name" : "%(app_name)s Application Owner",
           "metadata" : {
             "description" : "Application User for %(app_name)s"
           }
        }"""},
        "delete_user": {"mode": "DELETE", "path": "_security/user/%(app_name)s"},


        "get_api_keys": {"mode": "GET", "path": "_security/api_key?name=%(key_name)s"},
        "delete_api_key": {"mode": "DELETE", "path": "_security/api_key", "payload": """ { "name": "%(app_name)s-key", "owner": "true" }"""},
        "create_api_key": {"mode": "POST", "path": "_security/api_key", "payload": """{ "name": "%(app_name)s-key",
          "role_descriptors": {
              "application-role": {
                "indices": [ { "names": ["%(app_name)s_*"], "privileges": ["all"] } ]
             }
          },
          "metadata": {
              "application": ["%(app_name)s"],
              "environment": {
                  "level": 1,
                  "trusted": true,
                  "developer": "QED Systems Inc.",
                  "tags": ["dev", "staging"]
              }
          }}"""},

    }

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            choices=[
                "user",
                "role",
                "api_key",
            ],
            help="Operation Type; "
                 + "'role'=Create / Delete / List Elasticsearch roles"
                 + "'user'=Create / Delete / List Elasticsearch users"
                 + "'api_key'=Create / Invalidate / List API Keys"
        )

        # ES Connection options
        parser.add_argument(
            "-eh",
            "--es_host",
            action="store",
            dest="elasticsearch_host",
            default="localhost",
            help="Elasticsearch host name",
        )

        parser.add_argument(
            "-ep",
            "--es_port",
            action="store",
            dest="elasticsearch_port",
            default="9200",
            help="Elasticsearch server port",
        )

        parser.add_argument(
            "-U",
            "--es_username",
            action="store",
            dest="elasticsearch_username",
            default="",
            help="Username for Elasticsearch API calls",
        )

        parser.add_argument(
            "-P",
            "--es_password",
            action="store",
            dest="elasticsearch_password",
            default=None,
            help="Password for Elasticsearch API calls",
        )

        # Actions
        parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            dest="delete",
            default=False,
            help="Set to True to delete resources matching the key name. Default False",
        )

        parser.add_argument(
            "-c",
            "--create",
            action="store_true",
            dest="create",
            default=False,
            help="Set to True to create a user or API key with the given name. Default False",
        )

        parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            dest="list_values",
            default=False,
            help="Set to True to list all resource matching the given name. Default False",
        )

        parser.add_argument(
            "-vo",
            "--valid_only",
            action="store_true",
            dest="valid",
            default=False,
            help="Set to True(Default) to only list valid api keys.",
        )

        parser.add_argument(
            "-n",
            "--name",
            action="store",
            dest="name",
            default="",
            help="Name of ES user",
        )

        parser.add_argument(
            "-a",
            "--app_name",
            action="store",
            dest="app_name",
            default="",
            help="Name of ES API app name",
        )

        parser.add_argument(
            "-ap",
            "--app_user_password",
            action="store",
            dest="app_user_password",
            default="",
            help="Password for the Application User",
        )

    def _get_headers(self):
        headers = urllib3.util.make_headers(basic_auth="%s:%s"%(self.es_connection_parameters["username"],
                                                                self.es_connection_parameters["password"]),
                                            disable_cache=True)
        headers['Content-Type'] =  'application/json'
        return headers

    def _make_es_call(self, endpoint_name, parameters):
        # use the opener to fetch a URL

        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=self.es_connection_parameters["cert_location"])
        headers = self._get_headers()
        endpoint = self.endpoints[endpoint_name]

        endpoint_str = endpoint["path"] % parameters if parameters else endpoint["path"]
        url = "https://%s:%s/%s" % (self.es_connection_parameters["host"] ,
                                    self.es_connection_parameters["port"], endpoint_str)

        if "payload" in endpoint and endpoint["payload"] and endpoint["mode"] != "GET":
            payload_bytes = ( re.compile(r"\n").sub("", endpoint["payload"]) %parameters if parameters else endpoint["payload"]).encode()
        else:
            payload_bytes = None
        # print("Payload: %s" % payload_bytes)

        response = http.request(endpoint["mode"], url=url, headers=headers, body=payload_bytes)
        return json.loads(response.data)


    # Get API Keys for the give app_name
    def get_api_keys(self, app_name, valid_only=False):
        response = self._make_es_call("get_api_keys", {"key_name": "%s-key" % app_name})
        if valid_only:
            response["api_keys"] = list(filter(lambda item: not item["invalidated"], response["api_keys"]))
        print(json.dumps(response, indent=4, sort_keys=True))


    # Get API Keys for the give app_name
    def create_api_key(self, app_name):
        response = self._make_es_call("create_api_key", {"app_name": app_name})
        print(json.dumps(response, indent=4, sort_keys=True))

    def delete_api_key(self, app_name):
        response = self._make_es_call("delete_api_key", {"app_name": app_name})
        print(json.dumps(response, indent=4, sort_keys=True))

    def get_users(self, app_name):
        if app_name:
            response = self._make_es_call("get_user", {"app_name": app_name})
            print(json.dumps(response, indent=4, sort_keys=True))
        else:
            response = self._make_es_call("get_users", None)
            for key in sorted(response.keys()):
                print(key)


    def create_user(self, app_name, password):
        if not app_name or not password:
            print("app_name and app_user_password options required")
            exit(1)
        response = self._make_es_call("create_user", {"app_name": app_name,
                                                      "password": password})
        print(json.dumps(response, indent=4, sort_keys=True))

    def delete_user(self, app_name):
        response = self._make_es_call("delete_user", {"app_name": app_name})
        print(json.dumps(response, indent=4, sort_keys=True))

    def get_roles(self, role_name):
        if role_name:
            print("Role name: %s" % role_name)
            response = self._make_es_call("get_role", {"role_name": role_name})
        else:
            response = self._make_es_call("get_roles", None)
        keys = sorted(response.keys())
        print(json.dumps(response, indent=4, sort_keys=True))
        for key in keys:
            print(key)
        # print(json.dumps(response, indent=4, sort_keys=True))

    def create_role(self, app_name):
        response = self._make_es_call("create_role", {"role_name": "%s-user" % app_name, "app_name": app_name})
        print(json.dumps(response, indent=4, sort_keys=True))

    def delete_role(self, app_name, role_name):
        response = self._make_es_call("delete_role", {"role_name": "%s-user" % app_name if app_name else role_name})
        print(json.dumps(response, indent=4, sort_keys=True))

# Tries to set the ES admin credentials. Uses the command line values if provided,
# otherwise tries the values set in the .settings_es_admin file
    def _set_es_connection_parameters(self, options):
        if options["elasticsearch_username"]:
            self.es_connection_parameters["username"] = options["elasticsearch_username"]
        elif settings.setting_exists("ES_ADMIN_USER"):
            self.es_connection_parameters["username"] = settings.ES_ADMIN_USER
        else:
            print("ES Admin Username must be set in settings file or on the command line.")
            exit(1)

        if options["elasticsearch_password"]:
            self.es_connection_parameters["password"] = options["elasticsearch_password"]
        elif settings.setting_exists("ES_ADMIN_PASSWORD"):
            self.es_connection_parameters["password"] = settings.ES_ADMIN_PASSWORD
        else:
            print("ES Admin password must be set in settings file or on the command line.")
            exit(1)


    def handle(self,  *args, **options):
        print(options["operation"])
        self._set_es_connection_parameters(options)

        if options["operation"] == "user":
            if options["list_values"]:
                self.get_users(options["app_name"])
            elif options["create"]:
                self.create_role(options["app_name"])
                self.create_user(app_name=options["app_name"], password=options["app_user_password"])
            elif options["delete"]:
                self.delete_user(app_name=options["app_name"])
            pass

        elif options["operation"] == "role":
            if options["list_values"]:
                self.get_roles(options["name"])
            elif options["create"]:
                self.create_role(options["app_name"])
            elif options["delete"]:
                self.delete_role(options["app_name"], options["name"])

        elif options["operation"] == "api_key":
            if not options["app_name"]:
                print("Must specify app name using --app_name option")
                exit(1)

            if options["create"]:
                self.create_api_key(
                    app_name=options["app_name"]
                )
            elif options["delete"]:
                self.delete_api_key(app_name=options["app_name"])
            elif options["list_values"]:
                self.get_api_keys(app_name=options["app_name"],
                                  valid_only=options["valid"])
            else:
                print("Must specify one of --create, --delete or --list")

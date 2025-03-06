"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import psycopg2

# import the basic django settings here, don't use the Arches system_settings module
# because it makes database calls that don't necessarily work at this stage
from django.apps import apps
from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from arches.management.commands.utils import get_yn_input


class Command(BaseCommand):
    """
    Command to setup and refresh the database. Can be used initially to create
    the database for the first time, or iteratively to wipe and recreate it
    during development.
    """

    def add_arguments(self, parser):

        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help='used to force a yes answer to any user input "continue? y/n" prompt',
        )

        parser.add_argument(
            "-dev",
            "--dev",
            action="store_true",
            dest="dev",
            help="Add users for development",
        )

    def handle(self, *args, **options):

        if options["force"] is False:
            proceed = get_yn_input(
                msg="Are you sure you want to destroy and rebuild your database?",
                default="N",
            )
            if not proceed:
                exit()

        self.setup_db(development=options["dev"])

    def get_connection(self):
        """This method acquires a connection to the database, first trying to use
        separate PG_SUPERUSER and PG_SUPERUSER_PW credentials, and if they are not
        provided then it falls back on the default credentials in DATABASES."""

        db = settings.DATABASES["default"]

        # Attempt to use extra credentials from settings. If these don't exist
        # or are blank, revert to the default user/password credentials.
        try:
            if settings.PG_SUPERUSER != "" and settings.PG_SUPERUSER_PW != "":
                username = settings.PG_SUPERUSER
                password = settings.PG_SUPERUSER_PW
            else:
                username = db["USER"]
                password = db["PASSWORD"]
        except AttributeError:
            username = db["USER"]
            password = db["PASSWORD"]

        conn_string = "dbname={} user={} password={} host={} port={}".format(
            username, username, password, db["HOST"], db["PORT"]
        )

        try:
            # Connect directly to the user's database. This should work in most
            # superuser contexts.
            conn = psycopg2.connect(conn_string)
        except psycopg2.OperationalError as e:
            # If that connection fails, try connecting to the Arches database
            # itself. This is for non-superusers for whom the database has
            # already been created.
            try:
                # print conn_string
                conn_string = conn_string.replace(
                    "dbname=" + username, "dbname=" + db["NAME"]
                )
                conn = psycopg2.connect(conn_string)
            except psycopg2.OperationalError as e:
                # If that connection fails, this is probably a non-superuser
                # whose database has not yet been created.
                safestr = " ".join(
                    [i for i in conn_string.split(" ") if not i.startswith("password")]
                )
                print(str(e))
                print("Error connecting to db with these settings: " + safestr)
                print(
                    "\nHave you created the database yet? The quickest way to do so is to supply Postgres "
                    "superuser credentials in the PG_SUPERUSER and PG_SUPERUSER_PW settings, and then "
                    "re-run this same command."
                )
                exit()

        cursor = conn.cursor()
        cursor.execute(
            "SELECT rolcreatedb FROM pg_roles WHERE rolname = '{}'".format(username)
        )
        cancreate = cursor.fetchone()[0]

        cursor.execute(
            "SELECT rolsuper FROM pg_roles WHERE rolname = '{}'".format(username)
        )
        superuser = cursor.fetchone()[0]

        # autocommit false
        conn.set_isolation_level(0)
        return {"connection": conn, "can_create_db": any([cancreate, superuser])}

    def reset_db(self, cursor):

        # flush is needed here to remove the admin user from the auth tables
        management.call_command("flush", "--noinput")

        # unapply all of the Arches migrations (the Arches "app" is labeled "models")
        management.call_command(
            "migrate", fake=True, app_label="models", migration_name="zero"
        )

        # get the table names for all Arches models and then drop these tables
        arches_models = apps.get_app_config("models").get_models()
        table_names = [i._meta.db_table for i in arches_models]
        for t in table_names:
            cursor.execute("DROP TABLE IF EXISTS {} CASCADE".format(t))

    def drop_and_recreate_db(self, cursor):

        arches_db = settings.DATABASES["default"]

        print("Drop and recreate the database...")
        terminate_sql = """
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
    WHERE datname IN ('{}', '{}');""".format(
            arches_db["NAME"], arches_db["POSTGIS_TEMPLATE"]
        )
        print(terminate_sql)
        cursor.execute(terminate_sql)

        drop_query = """
DROP DATABASE IF EXISTS {0};""".format(
            arches_db["NAME"]
        )
        print(drop_query)
        cursor.execute(drop_query)

        create_query = """
CREATE DATABASE {}
    WITH OWNER = {}
        ENCODING = 'UTF8'
        CONNECTION LIMIT=-1
        TEMPLATE = {};""".format(
            arches_db["NAME"], arches_db["USER"], arches_db["POSTGIS_TEMPLATE"]
        )
        print(create_query + "\n")

        try:
            cursor.execute(create_query)
        except psycopg2.ProgrammingError as e:
            print(e.pgerror)
            if "template database" in e.pgerror:
                msg = """It looks like your PostGIS template database is not correctly referenced in
settings.py/settings_local.py, or it has not yet been created.

To create it, use:

    psql -U {0} -c "CREATE DATABASE {1};"
    psql -U {0} -d {1} -c "CREATE EXTENSION postgis;"
""".format(
                    arches_db["USER"], arches_db["POSTGIS_TEMPLATE"]
                )
                print(msg)
            exit()

    def setup_db(self, development=False):
        """
        Drops and re-installs the database found at "arches_<package_name>"
        WARNING: This will destroy data
        """

        conninfo = self.get_connection()
        conn = conninfo["connection"]
        can_create_db = conninfo["can_create_db"]

        cursor = conn.cursor()
        if can_create_db is True:
            self.drop_and_recreate_db(cursor)
        else:
            self.reset_db(cursor)
        # delete existing indexes
        management.call_command("es", operation="delete_indexes")

        # setup initial Elasticsearch indexes
        management.call_command("es", operation="setup_indexes")

        management.call_command("createcachetable")
        management.call_command("migrate")

        # import system settings graph and any saved system settings data
        settings_graph = os.path.join(
            settings.ROOT_DIR,
            "db",
            "system_settings",
            "Arches_System_Settings_Model.json",
        )
        management.call_command(
            "packages", operation="import_graphs", source=settings_graph
        )

        management.call_command("graph", operation="publish")

        settings_data = os.path.join(
            settings.ROOT_DIR, "db", "system_settings", "Arches_System_Settings.json"
        )
        management.call_command(
            "packages",
            operation="import_business_data",
            source=settings_data,
            overwrite="overwrite",
        )

        settings_data_local = settings.SYSTEM_SETTINGS_LOCAL_PATH

        if os.path.isfile(settings_data_local):
            management.call_command(
                "packages",
                operation="import_business_data",
                source=settings_data_local,
                overwrite="overwrite",
            )

        if development:
            management.call_command("add_test_users")

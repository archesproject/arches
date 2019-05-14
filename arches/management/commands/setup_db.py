'''
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
'''

import os
import psycopg2
# import the basic django settings here, don't use the Arches system_settings module
# because it makes database calls that don't necessarily work at this stage
from django.apps import apps
from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from arches.db.install import truncate_db
from arches.app.search.mappings import prepare_terms_index, prepare_resource_relations_index
from arches.management.commands.utils import get_yn_input


class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """

    def add_arguments(self, parser):

        parser.add_argument('--force', action='store_true', default=False,
                            help='used to force a yes answer to any user input "continue? y/n" prompt')

    def handle(self, *args, **options):

        if options["force"] is False:
            proceed = get_yn_input(msg="Are you sure you want to destroy and rebuild your database?", default="N")
            if not proceed:
                exit()

        self.setup_db()

    def get_admin_connection(self):

        db = settings.DATABASES['default']

        # Attempt to use extra credentials from settings. If these don't exist
        # or are blank, revert to the default user/password credentials.
        try:
            if settings.PG_SUPERUSER != "" and settings.PG_SUPERUSER_PW != "":
                username = settings.PG_SUPERUSER
                password = settings.PG_SUPERUSER_PW
            else:
                username = db['USER']
                password = db['PASSWORD']
        except AttributeError:
            username = db['USER']
            password = db['PASSWORD']

        conn_string = "dbname={} user={} password={} host={} port={}".format(
            username, username, password, db['HOST'], db['PORT']
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
                conn_string = conn_string.replace("dbname="+username, "dbname="+db['NAME'])
                conn = psycopg2.connect(conn_string)
            except psycopg2.OperationalError as e:
                # If that connection fails, this is probably a non-superuser
                # whose database has not yet been created.
                safestr = " ".join([i for i in conn_string.split(" ") if not i.startswith("password")])
                print("Error connecting to db with these settings: "+safestr)
                print(str(e))
                exit()

        # autocommit false
        conn.set_isolation_level(0)
        return conn

    def reset_db(self, cursor):

        # flush is needed here to remove the admin user from the auth tables
        management.call_command("flush", "--noinput")

        # unapply all of the Arches migrations (the Arches "app" is labeled "models")
        management.call_command("migrate", fake=True, app_label="models", migration_name="zero")

        # get the table names for all Arches models and then drop these tables
        arches_models = apps.get_app_config('models').get_models()
        table_names = [i._meta.db_table for i in arches_models]
        for t in table_names:
            cursor.execute("DROP TABLE IF EXISTS {} CASCADE".format(t))

    def drop_and_recreate_db(self, cursor):

        arches_db = settings.DATABASES['default']
        try:
            cursor.execute("SELECT pg_terminate_backend(pid) from pg_stat_activity where datname={0};".format(
                arches_db['NAME']))
        except psycopg2.ProgrammingError as e:
            pass

        drop_query = """
DROP DATABASE IF EXISTS {0};
""".format(arches_db['NAME'])
        print("Dropping old database..." + drop_query)
        cursor.execute(drop_query)
        print("    done")

        create_query = """
CREATE DATABASE {}
    WITH OWNER = {}
        ENCODING = 'UTF8'
        CONNECTION LIMIT=-1
        TEMPLATE = {};
""".format(arches_db['NAME'], arches_db['USER'], arches_db['POSTGIS_TEMPLATE'])
        print('Creating new database... ' + create_query)
        cursor.execute(create_query)

    def setup_db(self):
        """
        Drops and re-installs the database found at "arches_<package_name>"
        WARNING: This will destroy data
        """

        conn = self.get_admin_connection()
        cursor = conn.cursor()

        # figure out if this is a superuser or not
        cursor.execute("select current_setting('is_superuser')")
        superuser = True if cursor.fetchone() == ("on",) else False

        if superuser:
            self.drop_and_recreate_db(cursor)
        else:
            self.reset_db(cursor)

        # delete and setup initial Elasticsearch indexes
        management.call_command('es', operation='delete_indexes')
        prepare_terms_index(create=True)
        prepare_resource_relations_index(create=True)

        # run all migrations
        management.call_command('migrate')

        # import system settings graph and any saved system settings data
        settings_graph = os.path.join(settings.ROOT_DIR, 'db', 'system_settings', 'Arches_System_Settings_Model.json')
        management.call_command("packages", operation="import_graphs", source=settings_graph)

        settings_data = os.path.join(settings.ROOT_DIR, 'db', 'system_settings', 'Arches_System_Settings.json')
        management.call_command("packages", operation="import_business_data", source=settings_data, overwrite=True)

        settings_data_local = settings.SYSTEM_SETTINGS_LOCAL_PATH

        if os.path.isfile(settings_data_local):
            management.call_command("packages", operation="import_business_data", source=settings_data_local,
                                    overwrite=True)

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
from contextlib import contextmanager

from django.test import TestCase
from arches.app.models.graph import Graph
from arches.app.models.models import DDataType, Ontology
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from tests import test_settings
from arches.app.utils.context_processors import app_settings
from django.db import connection
from django.core import management
from django.test.runner import DiscoverRunner
from django.test.utils import captured_stdout

from arches.app.search.mappings import (
    prepare_terms_index,
    delete_terms_index,
    prepare_concepts_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
)

# these tests can be run from the command line via
# python manage.py test tests --settings="tests.test_settings"

OAUTH_CLIENT_ID = "AAac4uRQSqybRiO6hu7sHT50C4wmDp9fAmsPlCj9"
OAUTH_CLIENT_SECRET = "7fos0s7qIhFqUmalDI1QiiYj0rAtEdVMY4hYQDQjOxltbRCBW3dIydOeMD4MytDM9ogCPiYFiMBW6o6ye5bMh5dkeU7pg1cH86wF6B\
        ap9Ke2aaAZaeMPejzafPSj96ID"
CREATE_TOKEN_SQL = """
        INSERT INTO public.oauth2_provider_accesstoken(
            token, expires, scope, application_id, user_id, created, updated)
            VALUES ('{token}', '1-1-2068', 'read write', 44, {user_id}, '1-1-2018', '1-1-2018');
    """
DELETE_TOKEN_SQL = "DELETE FROM public.oauth2_provider_accesstoken WHERE application_id = 44;"
SYSTEM_SETINGS_GRAPH_ID = "ff623370-fa12-11e6-b98b-6c4008b05c4c"

class ArchesTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["debug_mode"] = True
        # Unless the user has something other than the Django default, give them
        # what they probably want.
        if kwargs["pattern"] == "test*.py":
            kwargs["pattern"] = "*.py"
        super().__init__(*args, **kwargs)

    def setup_databases(self, **kwargs):
        ret = super().setup_databases(**kwargs)

        app_settings()  # adds languages to system
        prepare_terms_index(create=True)
        prepare_concepts_index(create=True)
        prepare_search_index(create=True)

        return ret

    def teardown_databases(self, old_config, **kwargs):
        delete_terms_index()
        delete_concepts_index()
        delete_search_index()

        super().teardown_databases(old_config, **kwargs)

class ArchesTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(ArchesTestCase, self).__init__(*args, **kwargs)
        if settings.DEFAULT_BOUNDS is None:
            management.call_command("migrate")
            if not Graph.objects.filter(pk=SYSTEM_SETINGS_GRAPH_ID).exists():
                with open(os.path.join("tests/fixtures/system_settings/Arches_System_Settings_Model.json"), "r") as f:
                    archesfile = JSONDeserializer().deserialize(f)
                ResourceGraphImporter(archesfile["graph"], True)
                management.call_command("graph", ["publish"])
                BusinessDataImporter("tests/fixtures/system_settings/Arches_System_Settings_Local.json").import_business_data()
            settings.update_from_db()

    @classmethod
    def loadOntology(cls):
        ontologies_count = Ontology.objects.exclude(ontologyid__isnull=True).count()
        if ontologies_count == 0:
            management.call_command("load_ontology", source=test_settings.ONTOLOGY_PATH, verbosity=0)

    @classmethod
    def ensure_resource_test_model_loaded(cls):
        resource_test_model_graph_id = "c9b37a14-17b3-11eb-a708-acde48001122"
        custom_string_datatype_filename = os.path.join(
            test_settings.TEST_ROOT,
            "fixtures",
            "datatypes",
            "extended_string_datatype.py",
        )

        if not DDataType.objects.filter(datatype="extended-string-datatype").exists():
            management.call_command("datatype", "register", source=custom_string_datatype_filename, verbosity=0)
        if not Graph.objects.filter(pk=resource_test_model_graph_id).exists():
            for path in test_settings.RESOURCE_GRAPH_LOCATIONS:
                with captured_stdout():
                    management.call_command("packages", operation="import_graphs", source=path, verbosity=0)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cursor = connection.cursor()
        sql = """
            INSERT INTO public.oauth2_provider_application(
                id, client_id, redirect_uris, client_type, authorization_grant_type,
                client_secret,
                name, user_id, skip_authorization, created, updated, algorithm)
            VALUES (
                44, '{oauth_client_id}', 'http://localhost:8000/test', 'public', 'client-credentials',
                '{oauth_client_secret}',
                'TEST APP', {user_id}, false, '1-1-2000', '1-1-2000', '{jwt_algorithm}');
        """

        sql = sql.format(
            user_id=1,
            oauth_client_id=OAUTH_CLIENT_ID,
            oauth_client_secret=OAUTH_CLIENT_SECRET,
            jwt_algorithm=test_settings.JWT_ALGORITHM,
        )
        cursor.execute(sql)

    @classmethod
    def tearDownClass(cls):
        cursor = connection.cursor()
        sql = "DELETE FROM public.oauth2_provider_application WHERE id = 44;"
        cursor.execute(sql)
        super().tearDownClass()

    @classmethod
    def deleteGraph(cls, root):
        graph = Graph.objects.get(graphid=str(root))
        graph.delete()


@contextmanager
def sync_overridden_test_settings_to_arches():
    """Django's @override_settings test util acts on django.conf.settings,
    which is not enough for us, because we use SystemSettings at runtime.

    This context manager swaps in the overridden django.conf.settings for SystemSettings.
    """
    from django.conf import settings as patched_settings

    original_settings_wrapped = settings._wrapped
    try:
        settings._wrapped = patched_settings._wrapped
        yield
    finally:
        settings._wrapped = original_settings_wrapped

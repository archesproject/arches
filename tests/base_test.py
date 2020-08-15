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
from django.test import TestCase
from arches.app.models.graph import Graph
from arches.app.models.models import Ontology
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from tests import test_settings
from django.db import connection
from django.contrib.auth.models import User
from django.core import management
from arches.app.search.mappings import (
    prepare_terms_index,
    delete_terms_index,
    prepare_concepts_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
    prepare_resource_relations_index,
    delete_resource_relations_index,
)

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"

OAUTH_CLIENT_ID = "AAac4uRQSqybRiO6hu7sHT50C4wmDp9fAmsPlCj9"
OAUTH_CLIENT_SECRET = "7fos0s7qIhFqUmalDI1QiiYj0rAtEdVMY4hYQDQjOxltbRCBW3dIydOeMD4MytDM9ogCPiYFiMBW6o6ye5bMh5dkeU7pg1cH86wF6B\
        ap9Ke2aaAZaeMPejzafPSj96ID"
CREATE_TOKEN_SQL = """
        INSERT INTO public.oauth2_provider_accesstoken(
            token, expires, scope, application_id, user_id, created, updated)
            VALUES ('{token}', '1-1-2068', 'read write', 44, {user_id}, '1-1-2018', '1-1-2018');
    """


def setUpTestPackage():
    """
    see https://nose.readthedocs.io/en/latest/writing_tests.html#test-packages
    this is called from __init__.py
    """

    cursor = connection.cursor()
    sql = """
        INSERT INTO public.oauth2_provider_application(
            id,client_id, redirect_uris, client_type, authorization_grant_type,
            client_secret,
            name, user_id, skip_authorization, created, updated)
        VALUES (
            44,'{oauth_client_id}', 'http://localhost:8000/test', 'public', 'client-credentials',
            '{oauth_client_secret}',
            'TEST APP', {user_id}, false, '1-1-2000', '1-1-2000');
    """

    sql = sql.format(user_id=1, oauth_client_id=OAUTH_CLIENT_ID, oauth_client_secret=OAUTH_CLIENT_SECRET)
    cursor.execute(sql)

    prepare_terms_index(create=True)
    prepare_concepts_index(create=True)
    prepare_search_index(create=True)
    prepare_resource_relations_index(create=True)


def tearDownTestPackage():
    """
    see https://nose.readthedocs.io/en/latest/writing_tests.html#test-packages
    this is called from __init__.py
    """

    delete_terms_index()
    delete_concepts_index()
    delete_search_index()
    delete_resource_relations_index()


def setUpModule():
    # This doesn't appear to be called because ArchesTestCase is never called directly
    # See setUpTestPackage above
    pass


def tearDownModule():
    # This doesn't appear to be called because ArchesTestCase is never called directly
    # See tearDownTestPackage above
    pass


class ArchesTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(ArchesTestCase, self).__init__(*args, **kwargs)
        if settings.DEFAULT_BOUNDS is None:
            management.call_command("migrate")
            with open(os.path.join("tests/fixtures/system_settings/Arches_System_Settings_Model.json"), "rU") as f:
                archesfile = JSONDeserializer().deserialize(f)
            ResourceGraphImporter(archesfile["graph"], True)
            BusinessDataImporter("tests/fixtures/system_settings/Arches_System_Settings_Local.json").import_business_data()
            settings.update_from_db()

    @classmethod
    def loadOntology(cls):
        ontologies_count = Ontology.objects.exclude(ontologyid__isnull=True).count()
        if ontologies_count == 0:
            management.call_command("load_ontology", source=test_settings.ONTOLOGY_PATH)

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def deleteGraph(cls, root):
        graph = Graph.objects.get(graphid=str(root))
        graph.delete()

    def setUp(self):
        pass

    def tearDown(self):
        pass

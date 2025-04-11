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
from pathlib import Path

from django.db import connection
from django.core import management
from django.test import TestCase
from django.test.utils import captured_stdout

from arches.app.models.graph import Graph
from arches.app.models.models import Ontology
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.i18n import LanguageSynchronizer
from tests import test_settings

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
DELETE_TOKEN_SQL = (
    "DELETE FROM public.oauth2_provider_accesstoken WHERE application_id = 44;"
)
SYSTEM_SETINGS_GRAPH_ID = "ff623370-fa12-11e6-b98b-6c4008b05c4c"


class ArchesTestCase(TestCase):
    graph_fixtures = []
    """
    Similar to TestCase.fixtures, but uses ResourceGraphImporter to avoid flushing.
    Uses the name of the .json file (case-sensitive), not graph name.
    """

    def __init__(self, *args, **kwargs):
        super(ArchesTestCase, self).__init__(*args, **kwargs)
        if settings.DEFAULT_BOUNDS is None:
            management.call_command("migrate")
            if not Graph.objects.filter(pk=SYSTEM_SETINGS_GRAPH_ID).exists():
                with open(
                    os.path.join(
                        "tests/fixtures/system_settings/Arches_System_Settings_Model.json"
                    ),
                    "r",
                ) as f:
                    archesfile = JSONDeserializer().deserialize(f)
                ResourceGraphImporter(archesfile["graph"], True)
                management.call_command("graph", ["publish"])
                BusinessDataImporter(
                    "tests/fixtures/system_settings/Arches_System_Settings_Local.json"
                ).import_business_data()
            settings.update_from_db()

    @classmethod
    def loadOntology(cls):
        ontologies_count = Ontology.objects.exclude(ontologyid__isnull=True).count()
        if ontologies_count == 0:
            management.call_command(
                "load_ontology", source=test_settings.ONTOLOGY_PATH, verbosity=0
            )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

        with connection.cursor() as cursor:
            cursor.execute(sql)

    @classmethod
    def setUpTestData(cls):
        LanguageSynchronizer.synchronize_settings_with_db(update_published_graphs=False)
        cls.loadOntology()
        if not cls.graph_fixtures:
            return
        for path in test_settings.RESOURCE_GRAPH_LOCATIONS:
            file_paths = [
                file_path
                for file_path in os.listdir(path)
                if file_path.endswith(".json")
                and Path(file_path).stem in cls.graph_fixtures
            ]
            for file_path in file_paths:
                with captured_stdout():
                    with open(os.path.join(path, file_path), "r") as f:
                        archesfile = JSONDeserializer().deserialize(f)
                        errs, importer = ResourceGraphImporter(
                            archesfile["graph"], overwrite_graphs=True
                        )

    @classmethod
    def legacy_load_testing_package(cls):
        """Do not write new tests with this method."""
        test_concepts_path = (
            Path(test_settings.REFERENCE_DATA_FIXTURE_LOCATION) / "concepts"
        )
        test_collections_path = (
            Path(test_settings.REFERENCE_DATA_FIXTURE_LOCATION) / "collections"
        )
        test_package_path = Path(test_settings.REFERENCE_DATA_FIXTURE_LOCATION).parent

        with captured_stdout():
            management.call_command(
                "packages",
                [
                    "-o",
                    "import_reference_data",
                    "-s",
                    test_concepts_path / "Test-scheme.xml",
                ],
            )
            management.call_command(
                "packages",
                [
                    "-o",
                    "import_reference_data",
                    "-s",
                    test_concepts_path / "4.3 Test RDM Thesaurus.xml",
                ],
            )
            management.call_command(
                "packages",
                [
                    "-o",
                    "import_reference_data",
                    "-s",
                    test_collections_path / "Test-scheme-collections.xml",
                ],
            )
            management.call_command(
                "packages",
                [
                    "-o",
                    "import_reference_data",
                    "-s",
                    test_collections_path / "4.3 Test RDM collections.xml",
                ],
            )
            management.call_command(
                "packages",
                [
                    "-o",
                    "load_package",
                    "-s",
                    test_package_path,
                    "-ow",
                    "True",
                    "-y",
                ],
            )

        path_to_cheesy_image = Path(settings.MEDIA_ROOT) / "uploadedfiles" / "test.png"
        cls.addClassCleanup(os.unlink, path_to_cheesy_image)

    @classmethod
    def tearDownClass(cls):
        sql = "DELETE FROM public.oauth2_provider_application WHERE id = 44;"
        with connection.cursor() as cursor:
            cursor.execute(sql)
        super().tearDownClass()

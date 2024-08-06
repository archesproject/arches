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

import json
import shutil
import os
import uuid

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db import connection
from django.http import HttpRequest
from django.test import TransactionTestCase

from arches.app.etl_modules.branch_excel_importer import BranchExcelImporter
from arches.app.etl_modules.bulk_edit_concept import BulkConceptEditor
from arches.app.models.system_settings import settings
from arches.app.models.models import EditLog, ETLModule
from arches.app.models.graph import Graph
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as resource_graph_importer,
)
from arches.app.utils.i18n import LanguageSynchronizer
from arches.app.utils.skos import SKOSReader

# these tests can be run from the command line via
# python manage.py test tests.bulkdata.concept_edit_tests --settings="tests.test_settings"


class ConceptEditTests(TransactionTestCase):
    serialized_rollback = True

    def setUp(self):
        """setUpClass doesn't work because the rollback fixture is applied after that."""
        LanguageSynchronizer.synchronize_settings_with_db()

        for skospath in [
            "tests/fixtures/data/rdf_export_thesaurus.xml",
            "tests/fixtures/data/rdf_export_collections.xml",
        ]:
            skos = SKOSReader()
            rdf = skos.read_file(skospath)
            skos.save_concepts_from_skos(rdf)

        with open(
            os.path.join("tests/fixtures/resource_graphs/bulk_concept_test.json"), "r"
        ) as f:
            archesfile = JSONDeserializer().deserialize(f)
        resource_graph_importer(archesfile["graph"])
        graph = Graph.objects.get(graphid="2f4b00d2-29fb-486f-8623-9fb8d25b6de1")
        admin = User.objects.get(username="admin")
        graph.publish(user=admin)

        request = HttpRequest()
        request.method = "POST"
        request.user = User.objects.get(username="admin")
        load_id = "090bf2f0-ee96-4898-aab4-3aab97af0f7f"
        xls_file = "bulk_concept_test.xlsx"
        module_id = ETLModule.objects.get(slug="branch-excel-importer").pk

        details = {
            "result": {
                "summary": {
                    "name": "bulk_concept_test.xlsx",
                    "size": "6.45 kb",
                    "cumulative_files_size": 6605,
                    "files": {"bulk_concept_test.xlsx": {"size": "6.45 kb"}},
                }
            }
        }

        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO load_event (loadid, complete, etl_module_id, user_id) values (%s, FALSE, %s, 1)""",
                [
                    load_id,
                    module_id,
                ],
            )

        request.POST.__setitem__("load_id", load_id)
        request.POST.__setitem__("load_details", json.dumps(details))

        tmp_path = default_storage.path(
            os.path.join(settings.UPLOADED_FILES_DIR, "tmp", load_id)
        )
        xls_file = default_storage.path(
            os.path.join(settings.UPLOADED_FILES_DIR, xls_file)
        )

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        shutil.copy(xls_file, tmp_path)
        importer = BranchExcelImporter(request=request, loadid=load_id)
        importer.write(request)

    def test_write(self):
        load_id = "2046b340-baa3-4e80-9bab-dd2147a99818"
        node_id = "14e202da-514e-11ef-90df-323af0a1fd6a"
        graph_id = "2f4b00d2-29fb-486f-8623-9fb8d25b6de1"
        resource_ids = None
        unselected_tiles = [uuid.UUID("d14a3474-7ef8-4c84-abc5-4d12aebf98ea")]
        old_id = "beb53e39-8c48-4533-a6ef-b04882540be2"
        new_id = "9c721b1d-8a38-425e-9455-41ee5f5edfab"
        module_id = ETLModule.objects.get(slug="bulk_edit_concept").pk

        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO load_event (loadid, complete, etl_module_id, user_id) values (%s, FALSE, %s, 1)""",
                [load_id, module_id],
            )

        editor = BulkConceptEditor(loadid=load_id)
        editor.run_load_task(
            1,
            load_id,
            module_id,
            graph_id,
            node_id,
            resource_ids,
            unselected_tiles,
            old_id,
            new_id,
        )

        edits = EditLog.objects.filter(transactionid=load_id)
        edited = (
            len(edits) == 1
            and edits[0].oldvalue[node_id] == old_id
            and edits[0].newvalue[node_id] == new_id
        )

        self.assertTrue(edited)

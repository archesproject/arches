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
import os
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.http import HttpRequest
from django.test import TransactionTestCase

from arches.app.models.models import TileModel
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)
from arches.app.utils.i18n import LanguageSynchronizer
from django.contrib.auth.models import User

from arches.app.etl_modules.tile_excel_exporter import TileExcelExporter
from arches.app.etl_modules.tile_excel_importer import TileExcelImporter

from arches.app.etl_modules.base_import_module import FileValidationError

from arches.app.models.models import ETLModule, LoadEvent

# these tests can be run from the command line via
# python manage.py test tests.bulkdata.tile_excel_tests --settings="tests.test_settings"


class TileExcelTests(TransactionTestCase):
    serialized_rollback = True

    def setUp(self):
        LanguageSynchronizer.synchronize_settings_with_db()
        with open(
            Path(
                settings.TEST_ROOT,
                "fixtures",
                "resource_graphs",
                "Resource Test Model.json",
            ),
            "r",
        ) as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

    def test_import_tile_excel(self):
        tile_excel_importer = TileExcelImporter()
        load_event = LoadEvent.objects.create(
            user=User.objects.get(username="admin"),
            etl_module=ETLModule.objects.get(pk="b96b8078-23b7-484f-b9d0-8ca304a5f7b6"),
            status="running",
        )

        load_event.save()
        temp = tile_excel_importer.delete_from_default_storage
        tile_excel_importer.delete_from_default_storage = lambda *args: None
        with self.assertRaises(FileValidationError):
            tile_excel_importer.run_load_task(
                None, None, None, None, None, load_event.pk
            )
        tile_excel_importer.delete_from_default_storage = temp

    def test_cli(self):
        out = StringIO()
        excel_file_path = str(
            Path("tests", "fixtures", "data", "uploadedfiles", "tile_excel_test.xlsx")
        )
        call_command("etl", "tile-excel-importer", source=excel_file_path, stdout=out)
        self.assertIn("succeeded", out.getvalue())

        new_tiles = TileModel.objects.all()
        self.assertEqual(new_tiles.count(), 6)
        self.assertEqual(new_tiles.filter(sortorder=1).count(), 2)

    def test_export_with_orphaned_tile_node(self):
        """Export should not raise KeyError when tile tiledata contains a node
        UUID that is not in the graph (simulating a deleted node)."""
        excel_file_path = str(
            Path("tests", "fixtures", "data", "uploadedfiles", "tile_excel_test.xlsx")
        )
        call_command("etl", "tile-excel-importer", source=excel_file_path)

        fake_node_id = "00000000-0000-0000-0000-000000000000"
        name_nodegroup_id = "c9b37b7c-17b3-11eb-a708-acde48001122"

        # Add a fake node UUID to a tile's tiledata, simulating an orphaned
        # node reference after the node was deleted from the graph.
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tiles
                SET tiledata = tiledata || %s::jsonb
                WHERE tileid = (
                    SELECT tileid FROM tiles WHERE nodegroupid = %s LIMIT 1
                )
                """,
                [json.dumps({fake_node_id: "orphaned value"}), name_nodegroup_id],
            )
            self.assertEqual(
                cursor.rowcount,
                1,
                "Expected at least one tile in the name nodegroup from importer",
            )

        load_id = "5d288e76-ebd3-11ee-85b8-0242ac120005"
        graph_id = "c9b37a14-17b3-11eb-a708-acde48001122"
        graph_name = "Resource Test Model"
        file_name = "tile_exporter_orphaned_node_test"

        exported_file_path = os.path.join(
            "tests/fixtures/data/archestemp", file_name + ".zip"
        )
        self.addCleanup(
            lambda: (
                os.remove(exported_file_path)
                if os.path.exists(exported_file_path)
                else None
            )
        )

        exporter = TileExcelExporter(loadid=load_id)
        exporter.run_export_task(
            load_id=load_id,
            graph_id=graph_id,
            graph_name=graph_name,
            resource_ids=None,
            filename=file_name,
        )

        self.assertTrue(os.path.exists(exported_file_path))

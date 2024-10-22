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

from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)
from arches.app.utils.i18n import LanguageSynchronizer

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

    def test_cli(self):
        out = StringIO()
        excel_file_path = str(
            Path("tests", "fixtures", "data", "uploadedfiles", "tile_excel_test.xlsx")
        )
        call_command("etl", "tile-excel-importer", source=excel_file_path, stdout=out)
        self.assertIn("succeeded", out.getvalue())

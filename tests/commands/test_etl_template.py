# these tests can be run from the command line via
# python manage.py test tests.commands.test_etl_template --settings="tests.test_settings"

import os
import uuid

from django.core.management import call_command
from openpyxl import load_workbook

from arches.app.models.models import CardModel, Node, TileModel
from arches.management.commands.etl_template import create_tile_excel_workbook
from tests.base_test import ArchesTestCase


class ETLTemplateTests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model"]

    def test_sheet_title_replaces_slashes(self):
        card = CardModel.objects.get(name__en__iexact="Images-Files")
        card.name = "Images / Files"
        card.save()

        dest = "test_template.xlsx"
        self.addCleanup(os.remove, dest)
        call_command(
            "etl_template", template="tilexls", graph=str(card.graph.pk), dest=dest
        )

        wb = load_workbook(dest, read_only=True)
        self.assertIn("Images _ Files", wb.sheetnames)

    def test_trailing_columns_follow_node_columns(self):
        """Empty node values must not leave trailing column values behind in
        the node columns."""

        card = CardModel.objects.get(name__en__iexact="string")
        nodes = list(
            Node.objects.filter(nodegroup_id=card.nodegroup_id)
            .exclude(datatype="semantic")
            .values_list("pk", "alias")
        )
        tile = TileModel(
            resourceinstance_id=uuid.uuid4(),
            nodegroup_id=card.nodegroup_id,
            sortorder=0,
            data={str(nodeid): None for nodeid, _alias in nodes},
        )
        # create_tile_excel_workbook consumes the flattened tiles the tile
        # excel exporter builds: a raw tile row keyed by node alias rather
        # than by nodeid.
        exported_tile = {
            "tileid": tile.pk,
            "parenttileid": tile.parenttile_id,
            "resourceinstanceid": tile.resourceinstance_id,
            "nodegroupid": tile.nodegroup_id,
            "sortorder": tile.sortorder,
            "provisionaledits": tile.provisionaledits,
            **{alias: tile.data[str(nodeid)] for nodeid, alias in nodes},
        }

        wb = create_tile_excel_workbook(str(card.graph.pk), {"string": [exported_tile]})

        sheet = wb["string"]
        expected = {
            **{column: None for column in range(4, 4 + len(nodes))},
            len(nodes) + 4: tile.sortorder,
            len(nodes) + 5: tile.provisionaledits,
            len(nodes) + 6: str(tile.nodegroup_id),
        }
        for column, expected_value in expected.items():
            with self.subTest(column=column):
                print(sheet.cell(column=column, row=2).value, expected_value)
                self.assertEqual(sheet.cell(column=column, row=2).value, expected_value)

# these tests can be run from the command line via
# python manage.py test tests.commands.test_etl_template --settings="tests.test_settings"

import os
import uuid

from django.core.management import call_command
from openpyxl import load_workbook

from arches.app.models.models import CardModel, Node
from arches.management.commands.etl_template import (
    create_tile_excel_workbook,
    create_workbook,
)
from tests.base_test import ArchesTestCase


class ETLTemplateTests(ArchesTestCase):
    graph_fixtures = ["Data_Type_Model", "branch_excel_test"]

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

    def test_sheet_title_truncated_to_excel_limit(self):
        card = CardModel.objects.get(name__en__iexact="Images-Files")
        card.name = "A card name longer than the Excel sheet name limit"
        card.save()

        dest = "test_template.xlsx"
        self.addCleanup(os.remove, dest)
        call_command(
            "etl_template", template="tilexls", graph=str(card.graph.pk), dest=dest
        )

        wb = load_workbook(dest, read_only=True)
        self.assertIn("A card name longer than the E", wb.sheetnames)
        for sheetname in wb.sheetnames:
            self.assertLessEqual(len(sheetname), 31)

    def test_tile_sheets_with_duplicated_names_after_truncation_keep_their_own_tiles(
        self,
    ):
        cards = [
            CardModel.objects.get(name__en__iexact="Images-Files"),
            CardModel.objects.get(name__en__iexact="number"),
        ]
        tiles_by_card_name = {}
        tileid_by_node_alias = {}
        for i, card in enumerate(cards, start=1):
            card.name = f"A card name longer than the Excel sheet name limit {i}"
            card.save()
            node_alias = (
                Node.objects.exclude(datatype="semantic")
                .get(nodegroup_id=card.nodegroup_id)
                .alias
            )
            tileid = str(uuid.uuid4())
            tiles_by_card_name[str(card.name)] = [
                {
                    "tileid": tileid,
                    "parenttileid": None,
                    "resourceinstanceid": str(uuid.uuid4()),
                    "nodegroupid": card.nodegroup_id,
                    "sortorder": 0,
                    "provisionaledits": None,
                    node_alias: f"value {i}",
                }
            ]
            tileid_by_node_alias[node_alias] = tileid

        graph_id = str(cards[0].graph_id)
        wb = create_tile_excel_workbook(graph_id, tiles_by_card_name)

        for title in (
            "A card name longer than the E",
            "A card name longer than the E1",
        ):
            sheet = wb[title]
            self.assertEqual(
                sheet.max_row, 2
            )  # check the sheet has data from exactly one tile
            self.assertEqual(
                sheet["A2"].value, tileid_by_node_alias[sheet["D1"].value]
            )  # check correct tile included

    def test_branch_sheet_title_truncated_to_excel_limit(self):
        node = Node.objects.get(
            graph_id="a5c3946a-a9c0-4472-9191-ffc0f35a5901", alias="string"
        )
        node.alias = "a_node_alias_longer_than_the_excel_sheet_name_limit"
        node.save()

        dest = "test_template.xlsx"
        self.addCleanup(os.remove, dest)
        call_command(
            "etl_template", template="branchcsv", graph=str(node.graph_id), dest=dest
        )

        wb = load_workbook(dest, read_only=True)
        self.assertIn("a_node_alias_longer_than_the_", wb.sheetnames)
        for sheetname in wb.sheetnames:
            self.assertLessEqual(len(sheetname), 31)

    def test_branch_sheets_with_duplicated_names_after_truncation_keep_their_own_tiles(
        self,
    ):
        graph_id = "a5c3946a-a9c0-4472-9191-ffc0f35a5901"
        tiles_by_root_alias = {}
        tileid_by_node_alias = {}
        for i, alias in enumerate(["geometry", "string"], start=1):
            node = Node.objects.get(graph_id=graph_id, alias=alias)
            node.alias = f"a_node_alias_longer_than_the_excel_sheet_name_limit_{i}"
            node.save()
            tileid = str(uuid.uuid4())
            tiles_by_root_alias[node.alias] = [
                {
                    "resourceinstanceid": str(uuid.uuid4()),
                    "tileid": tileid,
                    "depth": 0,
                    "alias": node.alias,
                    "nodegroupid": node.nodegroup_id,
                    node.alias: f"value {i}",
                }
            ]
            tileid_by_node_alias[node.alias] = tileid

        wb = create_workbook(graph_id, tiles_by_root_alias)

        for title in (
            "a_node_alias_longer_than_the_",
            "a_node_alias_longer_than_the_1",
        ):
            sheet = wb[title]
            self.assertEqual(
                sheet.max_row, 3
            )  # check the sheet has a template row and data from exactly one tile
            self.assertEqual(
                sheet["B3"].value, tileid_by_node_alias[sheet["D2"].value]
            )  # check correct tile included

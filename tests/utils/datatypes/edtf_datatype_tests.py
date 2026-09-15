import json
import uuid
from types import SimpleNamespace
from unittest.mock import patch

from arches.app.datatypes.datatypes import DataTypeFactory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.edtf_datatype_tests --settings="tests.test_settings"


class EDTFDataTypeTests(ArchesTestCase):
    @patch("arches.app.datatypes.datatypes.models.Node.objects.get")
    def test_edtf_append_to_document(self, mock_get_node):
        mock_get_node.return_value = SimpleNamespace(config={})

        datatype = DataTypeFactory().get_instance("edtf")
        nodeid = str(uuid.uuid4())
        tile = SimpleNamespace(nodegroup_id=uuid.uuid4(), data={})
        document = {"dates": [], "date_ranges": []}

        datatype.append_to_document(
            document=document,
            nodevalue="2020-01-20",
            nodeid=nodeid,
            tile=tile,
        )

        with self.subTest("document contains one exact date"):
            self.assertEqual(len(document["dates"]), 1)

        with self.subTest("document contains no date ranges for exact date"):
            self.assertEqual(document["date_ranges"], [])

        with self.subTest("document nodegroup_id is string"):
            self.assertEqual(
                document["dates"][0]["nodegroup_id"], str(tile.nodegroup_id)
            )
            self.assertIsInstance(document["dates"][0]["nodegroup_id"], str)

        with self.subTest("tile value updated for advanced search"):
            self.assertEqual(tile.data[nodeid]["value"], "2020-01-20")

        with self.subTest("document payload is JSON serializable"):
            try:
                json.dumps(tile.data[nodeid])
            except (TypeError, ValueError) as exc:
                self.fail(f"Expected JSON-serializable document value, got: {exc}")

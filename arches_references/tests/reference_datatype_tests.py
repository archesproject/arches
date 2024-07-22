from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.tile import Tile
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test arches_references.tests.reference_datatype_tests --settings="tests.test_settings"

class ReferenceDataTypeTests(ArchesTestCase):
    def test_validate(self):
        reference = DataTypeFactory().get_instance("reference")

        for value in [
            "",
            [],
            [{}],  # reference has no 'uri'
            [{"uri": ""}],  # reference uri is empty
        ]:
            with self.subTest(reference_value=value):
                errors = reference.validate(value)
                self.assertTrue(len(errors) > 0)

        data = {
            "uri": "https://www.domain.com/label",
            "labels": [
                {
                    "id": "23b4efbd-2e46-4b3f-8d75-2f3b2bb96af2",
                    "value": "label",
                    "language_id": "en",
                    "valuetype_id": "prefLabel",
                },
                {
                    "id": "e8676242-f0c7-4e3d-b031-fded4960cd86",
                    "language_id": "de",
                    "valuetype_id": "prefLabel",
                },
            ],
        }

        errors = reference.validate(value=[data])  # label missing value property
        self.assertIsNotNone(errors)

        data["labels"][1]["value"] = "a label"
        data["labels"][1]["language_id"] = "en"

        errors = reference.validate(value=[data])  # too many prefLabels per language
        self.assertIsNotNone(errors)

        data["labels"][1]["value"] = "ein label"
        data["labels"][1]["language_id"] = "de"

        errors = reference.validate(value=[data])  # data should be valid
        self.assertTrue(len(errors) == 0)

    def test_tile_clean(self):
        reference = DataTypeFactory().get_instance("reference")
        nodeid = "72048cb3-adbc-11e6-9ccf-14109fd34195"
        resourceinstanceid = "40000000-0000-0000-0000-000000000000"
        data = [
            {
                "uri": "https://www.domain.com/label",
                "labels": [
                    {
                        "id": "23b4efbd-2e46-4b3f-8d75-2f3b2bb96af2",
                        "value": "label",
                        "language_id": "en",
                        "valuetype_id": "prefLabel",
                    },
                ],
                "listid": "fd9508dc-2aab-4c46-85ae-dccce1200035",
            }
        ]

        tile_info = {
            "resourceinstance_id": resourceinstanceid,
            "parenttile_id": "",
            "nodegroup_id": nodeid,
            "tileid": "",
            "data": {nodeid: {"en": data}},
        }

        tile1 = Tile(tile_info)
        reference.clean(tile1, nodeid)
        self.assertIsNotNone(tile1.data[nodeid])

        tile1.data[nodeid] = []
        reference.clean(tile1, nodeid)
        self.assertIsNone(tile1.data[nodeid])
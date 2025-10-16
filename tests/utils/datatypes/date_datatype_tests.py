import datetime

from arches.app.datatypes.datatypes import DataTypeFactory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.date_datatype_tests --settings="tests.test_settings"


class DateDataTypeTests(ArchesTestCase):

    sample_dates = [
        {"value": "2025", "format": "YYYY"},
        {"value": "2025-01", "format": "YYYY-MM"},
        {"value": "2025-01-01", "format": "YYYY-MM-DD"},
        {"value": "2025-03-25 13:47:11-0600", "format": "YYYY-MM-DD HH:mm:ssZ"},
    ]

    date_without_config = {"value": "2025-03-25T21:53:01.946977+0100", "format": None}

    date_formats_lookup = {
        "YYYY-MM-DD HH:mm:ssZ": "%Y-%m-%d %H:%M:%S%z",
        "YYYY-MM-DD": "%Y-%m-%d",
        "YYYY-MM": "%Y-%m",
        "YYYY": "%Y",
    }

    def test_string_validate(self):
        datatype = DataTypeFactory().get_instance("date")
        for date in self.sample_dates:
            with self.subTest(input=date["value"]):
                errors = datatype.validate(date["value"])
                self.assertEqual(len(errors), 0)

    def test_tile_transform(self, **kwarg):
        datatype = DataTypeFactory().get_instance("date")
        for date in self.sample_dates:
            config = {"dateFormat": date["format"]}
            print("config", config)
            with self.subTest(input=date):
                tile_value = datatype.transform_value_for_tile(date["value"], **config)
                self.assertEqual(tile_value, date["value"])
                # self.assertEqual(tile_value, tile_value)

    def test_tile_transform_withou_config(self, **kwarg):
        datatype = DataTypeFactory().get_instance("date")
        tile_value = datatype.transform_value_for_tile(
            self.date_without_config["value"]
        )
        date_value = datetime.datetime.strptime(tile_value, "%Y-%m-%d %H:%M:%S%z")
        self.assertEqual(date_value.year, 2025)

    def test_tile_transform_python(self):
        datatype = DataTypeFactory().get_instance("date")
        python_dates = [
            datetime.datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
            datetime.date(2025, 1, 1),
        ]
        for date in python_dates:
            with self.subTest(input=date):
                tile_value = datatype.transform_value_for_tile(date)
                date_value = datetime.datetime.strptime(
                    tile_value, "%Y-%m-%d %H:%M:%S%z"
                )
                self.assertEqual(date_value.year, 2025)

import datetime

from arches.app.datatypes.datatypes import DataTypeFactory
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.date_datatype_tests --settings="tests.test_settings"


class DateDataTypeTests(ArchesTestCase):

    sample_dates = [
        "-2025",
        "2025",
        "2025-01",
        "2025-01-01",
        "2025-03-25 13:47:11+0100",
        "2025-03-25T21:53:01.946977+0100",
    ]

    def test_string_validate(self):
        datatype = DataTypeFactory().get_instance("date")
        for date in self.sample_dates:
            with self.subTest(input=date):
                errors = datatype.validate(date)
                self.assertEqual(len(errors), 0)

    def test_tile_transform(self):
        datatype = DataTypeFactory().get_instance("date")
        python_dates = [
            datetime.datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
            datetime.date(2025, 1, 1),
        ]
        for date in (*self.sample_dates, *python_dates):
            with self.subTest(input=date):
                tile_value = datatype.transform_value_for_tile(date)
                date_value = datetime.datetime.strptime(
                    tile_value, "%Y-%m-%dT%H:%M:%S.%f%z"
                )
                self.assertEqual(date_value.year, 2025)

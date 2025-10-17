import datetime
from tests.base_test import ArchesTestCase
from zoneinfo import ZoneInfo
from django.test import override_settings
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.system_settings import settings

# these tests can be run from the command line via
# python manage.py test tests.utils.datatypes.date_datatype_tests --settings="tests.test_settings"


class DateDataTypeTests(ArchesTestCase):
    sample_dates = [
        {"value": "2025", "format": "YYYY"},
        {"value": "2025-01", "format": "YYYY-MM"},
        {"value": "2025-01-01", "format": "YYYY-MM-DD"},
        {"value": "2025-03-25 13:47:11-0600", "format": "YYYY-MM-DD HH:mm:ssZ"},
    ]

    dates_without_config = [
        {
            "value": "2025-03-25",
            "expected_format": "%Y-%m-%d",
        },  # valid node config dataFormat
        {
            "value": "2025-03-25T21:53:01.946977+0100",
            "expected_format": "%Y-%m-%d %H:%M:%S%z",
        },  # invalid node config dataFormat
    ]

    python_dates = [
        datetime.datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
        datetime.date(2025, 1, 1),
    ]

    timezone_dates = [
        "2025-03-25 06:47:11-0700",
        "2025-03-25 08:47:11-0500",
        "2025-03-25 08:47:11",
    ]

    time_zone = ZoneInfo(settings.TIME_ZONE)

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
            with self.subTest(input=date):
                tile_value = datatype.transform_value_for_tile(date["value"], **config)
                self.assertEqual(tile_value, date["value"])

    def test_tile_transform_without_config(self, **kwarg):
        datatype = DataTypeFactory().get_instance("date")
        for date in self.dates_without_config:
            with self.subTest(input=date):
                tile_value = datatype.transform_value_for_tile(date["value"])
                date_value = datetime.datetime.strptime(
                    tile_value, date["expected_format"]
                )
                self.assertEqual(date_value.year, 2025)

    def test_tile_transform_python(self):
        datatype = DataTypeFactory().get_instance("date")
        for date in self.python_dates:
            with self.subTest(input=date):
                tile_value = datatype.transform_value_for_tile(date)
                date_value = datetime.datetime.strptime(
                    tile_value, "%Y-%m-%d %H:%M:%S%z"
                )
                self.assertEqual(date_value.year, 2025)

    def test_set_timezone(self, **kwarg):
        datatype = DataTypeFactory().get_instance("date")

        los_angeles_date_format, _valid_la = datatype.get_valid_date_format(
            self.timezone_dates[0]
        )
        los_angeles_date = datetime.datetime.strptime(
            self.timezone_dates[0], los_angeles_date_format
        )

        chicago_date_format, _valid_chicago = datatype.get_valid_date_format(
            self.timezone_dates[1]
        )
        chicago_date = datetime.datetime.strptime(
            self.timezone_dates[1], chicago_date_format
        )

        los_angeles_date_tz = datatype.set_timezone(los_angeles_date)
        chicago_date_tz = datatype.set_timezone(chicago_date)

        self.assertEqual(los_angeles_date_tz, chicago_date_tz)

    @override_settings(DATE_IMPORT_EXPORT_FORMAT="%Y-%m-%d %H:%M:%S")
    def test_set_timezone_no_z(self, **kwarg):
        datatype = DataTypeFactory().get_instance("date")

        transformed_value = datatype.transform_value_for_tile(self.timezone_dates[2])
        value = datetime.datetime.strptime(self.timezone_dates[2], "%Y-%m-%d %H:%M:%S")
        value = value.astimezone(self.time_zone).strftime("%Y-%m-%d %H:%M:%S%z")
        self.assertEqual(transformed_value, value)

from django.test import SimpleTestCase

from arches.app.models.fields.i18n import I18n_JSON, I18n_String
from arches.app.utils.betterJSONSerializer import JSONSerializer

# these tests can be run from the command line via
# python manage.py test tests.utils.test_betterJSONSerializer --settings="tests.test_settings"


class TestBetterJSONSerializer(SimpleTestCase):
    def test_encode_i18n_json(self):
        serializer = JSONSerializer()
        json = I18n_JSON("{'trueLabel': {'en': 'Yes'}")
        encoded = serializer.encode(json)
        self.assertEqual(
            encoded, "\"{'trueLabel': {'en': 'Yes'}\"", "JSON must be double-quoted"
        )

    def test_encode_i18n_string(self):
        string = I18n_String()
        string["de"] = "German label"
        string["en"] = "English label"

        serializer = JSONSerializer()
        encoded = serializer.encode(string)
        self.assertEqual(encoded, '{"en": "English label", "de": "German label"}')

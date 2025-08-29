from arches.app.utils.string_utils import deserialize_json_like_string
from django.test import SimpleTestCase

# these tests can be run from the command line via
# python manage.py test tests.utils.test_string_utils --settings="tests.test_settings"


class StringUtilsTests(SimpleTestCase):
    def test_deserialize_json_like_string(self):
        cases = [
            {"type": "valid json", "value": '{"foo":"bar"}'},
            {"type": "single quotes", "value": "{'foo':'bar'}"},
            {"type": "excaped quotes", "value": '"{\\"cat\\": \\"miles\\"}"'},
            {"type": "apostrophes", "value": """{"foo":"bar's"}"""},
        ]

        for case in cases:
            with self.subTest(case=case):
                res = deserialize_json_like_string(case["value"])
                self.assertTrue(isinstance(res, dict))

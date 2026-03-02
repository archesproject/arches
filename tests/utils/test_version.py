from django.test import SimpleTestCase
from packaging.version import Version
from arches.version import get_complete_version


class VersionTests(SimpleTestCase):

    def test_string_final_version(self):
        result = get_complete_version("1.2.3")
        self.assertEqual(result, (1, 2, 3, "final", 0))

    def test_string_alpha_version(self):
        result = get_complete_version("1.2.3a1")
        self.assertEqual(result, (1, 2, 3, "alpha", 1))

    def test_string_beta_version(self):
        result = get_complete_version("1.2.3b2")
        self.assertEqual(result, (1, 2, 3, "beta", 2))

    def test_string_rc_version(self):
        result = get_complete_version("1.2.3rc3")
        self.assertEqual(result, (1, 2, 3, "rc", 3))

    def test_packaging_version_final(self):
        result = get_complete_version(Version("2.0.0"))
        self.assertEqual(result, (2, 0, 0, "final", 0))

    def test_tuple_passthrough(self):
        version_tuple = (3, 1, 0, "final", 0)
        result = get_complete_version(version_tuple)
        self.assertEqual(result, version_tuple)

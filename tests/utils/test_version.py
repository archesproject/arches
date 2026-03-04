import unittest
import arches

# these tests can be run from the command line via
# python manage.py test tests.utils.test_version --settings="tests.test_settings"


class VersionTupleTests(unittest.TestCase):

    def test_version_tuple_imported_from_arches(self):
        """VERSION exported by the package is a 5-tuple with the expected shape."""

        version_tuple = arches.VERSION
        self.assertIsInstance(version_tuple, tuple)
        self.assertEqual(len(version_tuple), 5)
        major, minor, micro, pre_type, pre_num = version_tuple
        self.assertIsInstance(major, int)
        self.assertIsInstance(minor, int)
        self.assertIsInstance(micro, int)
        self.assertIn(pre_type, ("alpha", "beta", "rc", "final"))
        self.assertIsInstance(pre_num, int)


if __name__ == "__main__":
    unittest.main()
